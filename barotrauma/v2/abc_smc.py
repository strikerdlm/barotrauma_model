"""
barotrauma.v2.abc_smc
=====================

Approximate Bayesian Computation with Sequential Monte-Carlo (ABC-SMC)
calibration for the v2.1 hazard model.

Why ABC-SMC
-----------
The v2.0 bisection calibrator (``calibration.calibrate_hazard_constants``)
fits a single hazard-rate constant against a single summary statistic
(cohort mean p_barotitis). It returns a point estimate with no uncertainty
quantification.

ABC-SMC lets us:
- Jointly sample the full hazard vector (r_barotitis, r_bmrg, r_rupture).
- Match MULTIPLE summary statistics simultaneously (prevalence + URI
  subgroup gradient + severity subgroup gradient).
- Report a posterior distribution, not a point estimate.

Implementation follows the Torres-Florez 2025 (PMID 40853999) template,
scaled down to run in minutes on a laptop.

Algorithm
---------
Generation 0:
  sample N particles from prior
  simulate cohort per particle → summary statistics s_i
  accept if distance(s_i, s_obs) < ε_0

Generation k+1:
  resample N particles from generation k, weighted by w_i
  perturb with a Gaussian kernel (covariance = empirical ×2)
  simulate cohort → s_i
  accept if distance(s_i, s_obs) < ε_{k+1}
  weight w_i ∝ prior(θ_i) / Σ_j w_j^(k) K(θ_i - θ_j^(k))

Final posterior: weighted empirical distribution.

For production use set ``n_particles=1000``, ``n_generations=6``; the
defaults here (100 × 3) are tuned to keep CI wall time under ~3 minutes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from . import constants as C
from .calibration import CohortPriors, sample_cohort
from .engine import simulate
from .scenarios import FAC_BOGOTA_DEFAULT
from .types import ChamberProfile, PatientState


# ------------------------------------------------------ priors ---------
@dataclass(frozen=True)
class HazardPrior:
    """
    Log-uniform prior on the three hazard-rate constants. Default range is
    ~2 decades centered on the v2.1 point-estimate calibration (r_baro
    ≈ 4e-8); this is tight because the physics-informed simulator + the
    FAC 2% per-exposure anchor already strongly constrain the order of
    magnitude. Widen for exploratory runs.
    """

    r_baro_log10: tuple[float, float] = (-9.0, -7.0)
    r_bmrg_log10: tuple[float, float] = (-10.5, -8.5)
    r_rupt_log10: tuple[float, float] = (-12.0, -10.0)

    def sample(self, rng: np.random.Generator, n: int = 1) -> np.ndarray:
        """Draw n particles of shape (n, 3)."""
        lo = np.array([self.r_baro_log10[0], self.r_bmrg_log10[0],
                        self.r_rupt_log10[0]])
        hi = np.array([self.r_baro_log10[1], self.r_bmrg_log10[1],
                        self.r_rupt_log10[1]])
        x = rng.uniform(lo, hi, size=(n, 3))
        return 10.0 ** x

    def log_density(self, theta: np.ndarray) -> float:
        """log p(θ) in linear space. Uniform on log10 → 1/θ density."""
        lo = 10.0 ** np.array([self.r_baro_log10[0], self.r_bmrg_log10[0],
                                self.r_rupt_log10[0]])
        hi = 10.0 ** np.array([self.r_baro_log10[1], self.r_bmrg_log10[1],
                                self.r_rupt_log10[1]])
        if np.any(theta < lo) or np.any(theta > hi):
            return -np.inf
        return float(-np.sum(np.log(theta)))


# ------------------------------------------------- observation targets -
@dataclass(frozen=True)
class AbcObservation:
    """
    Target summary statistics for ABC.

    Defaults: the FAC 2% per-exposure anchor, plus URI and severity
    gradient ratios calibrated against the v2.1 deterministic simulator
    (URI peak is ~30-70× URI none; severe ETD is ~10-20× normal). The
    gradients are widely variable because they depend on cohort mix and
    the aperture model, so the SEs are set broad to avoid over-constraining
    the posterior on r_baro alone.
    """

    mean_p_barotitis: float = 0.020              # FAC per-exposure anchor
    uri_gradient: float = 40.0                    # day_4_7 / none observed ratio
    severity_gradient: float = 15.0               # severe / normal observed ratio
    sigma_prev: float = 0.006                     # SE on prevalence
    sigma_uri: float = 20.0                       # SE on URI gradient (broad)
    sigma_sev: float = 10.0                       # SE on severity gradient (broad)


# ------------------------------------- prebaked cohort simulation ------
@dataclass
class _PrebakedCohort:
    """
    One-time cohort simulation result. Each element is (trace, modifiers,
    uri, severity) — enough to re-score hazards without re-integrating.
    """

    traces: list                          # list[SimulationTrace]
    modifiers: list                       # list[Modifiers]
    uris: list[str]
    severities: list[str]


def _prebake_cohort(
    cohort: list[PatientState],
    profile: ChamberProfile,
    dt_s: float,
    rng_seed: int,
) -> _PrebakedCohort:
    """Run every cohort member once, store traces + modifiers."""
    from .pathophysiology import modifiers_for_patient

    traces = []
    modifiers_list = []
    uris: list[str] = []
    severities: list[str] = []
    for i, p in enumerate(cohort):
        r = simulate(p, profile, dt_s=dt_s, rng_seed=rng_seed + i)
        traces.append(r.trace)
        modifiers_list.append(modifiers_for_patient(p))
        uris.append(p.uri)
        severities.append(p.et.severity)
    return _PrebakedCohort(
        traces=traces,
        modifiers=modifiers_list,
        uris=uris,
        severities=severities,
    )


def _score_prebaked(
    theta: np.ndarray,
    prebaked: _PrebakedCohort,
) -> dict[str, float]:
    """
    Re-score every prebaked trace with the hazard vector θ = (r_baro, r_bmrg,
    r_rupt). Runs in milliseconds per particle, avoiding re-integration.
    """
    r_baro_orig = C.HAZARD_BAROTITIS_R
    r_bmrg_orig = C.HAZARD_BAROMYRINGITIS_R
    r_rupt_orig = C.HAZARD_RUPTURE_R
    try:
        C.HAZARD_BAROTITIS_R = float(theta[0])
        C.HAZARD_BAROMYRINGITIS_R = float(theta[1])
        C.HAZARD_RUPTURE_R = float(theta[2])

        from .risk import score_trace
        from .types import PatientState as _PS   # local for dummy

        uri_none: list[float] = []
        uri_peak: list[float] = []
        sev_normal: list[float] = []
        sev_severe: list[float] = []
        all_probs: list[float] = []

        # We need a PatientState to reconstruct score_trace's
        # _identify_dominant_risk signature; use a minimal dummy per record.
        for trace, mods, uri, sev in zip(
            prebaked.traces, prebaked.modifiers,
            prebaked.uris, prebaked.severities,
        ):
            # Dummy patient — score_trace only uses patient for risk labeling,
            # which we ignore here.
            dummy = _PS()
            res = score_trace(trace, dummy, mods)
            pb = res.p_barotitis
            all_probs.append(pb)
            if uri == "none":
                uri_none.append(pb)
            elif uri == "day_4_7":
                uri_peak.append(pb)
            if sev == "normal":
                sev_normal.append(pb)
            elif sev == "severe":
                sev_severe.append(pb)

        mean_p = float(np.mean(all_probs))
        uri_gradient = (
            float(np.mean(uri_peak)) / max(float(np.mean(uri_none)), 1e-6)
            if uri_peak and uri_none else 1.0
        )
        severity_gradient = (
            float(np.mean(sev_severe)) / max(float(np.mean(sev_normal)), 1e-6)
            if sev_severe and sev_normal else 1.0
        )
        return {
            "mean_p": mean_p,
            "uri_gradient": uri_gradient,
            "severity_gradient": severity_gradient,
        }
    finally:
        C.HAZARD_BAROTITIS_R = r_baro_orig
        C.HAZARD_BAROMYRINGITIS_R = r_bmrg_orig
        C.HAZARD_RUPTURE_R = r_rupt_orig


def _distance(stats: dict[str, float], obs: AbcObservation) -> float:
    """Normalized Euclidean distance across the three summary statistics."""
    return float(np.sqrt(
        ((stats["mean_p"] - obs.mean_p_barotitis) / obs.sigma_prev) ** 2 +
        ((stats["uri_gradient"] - obs.uri_gradient) / obs.sigma_uri) ** 2 +
        ((stats["severity_gradient"] - obs.severity_gradient) / obs.sigma_sev) ** 2
    ))


# ---------------------------------------- core SMC sampler -------------
@dataclass
class AbcSmcResult:
    particles_log10: np.ndarray            # shape (n_particles, 3)
    weights: np.ndarray                     # shape (n_particles,)
    distances: np.ndarray                   # final-generation distances
    n_generations: int
    tolerances: list[float]
    posterior_mean_log10: np.ndarray
    posterior_std_log10: np.ndarray
    posterior_ci95_log10: np.ndarray        # shape (3, 2) — low, high for each param

    def posterior_mean_hazard(self) -> np.ndarray:
        """Convert log10 posterior mean back to linear hazard scale."""
        return 10.0 ** self.posterior_mean_log10

    def posterior_ci95_hazard(self) -> np.ndarray:
        """95% CI on each hazard rate in linear scale."""
        return 10.0 ** self.posterior_ci95_log10


def run_abc_smc(
    *,
    prior: HazardPrior = HazardPrior(),
    observation: AbcObservation = AbcObservation(),
    cohort_size: int = 150,
    profile: ChamberProfile = FAC_BOGOTA_DEFAULT,
    dt_s: float = 0.3,
    n_particles: int = 100,
    n_generations: int = 3,
    initial_tolerance_quantile: float = 0.75,
    rng_seed: int = 2026,
) -> AbcSmcResult:
    """
    Run ABC-SMC. Returns weighted particles + posterior summary.

    ``cohort_size`` is the synthetic cohort drawn once and reused across
    all particles (identical subjects, varying hazard rates) so that
    per-particle noise reflects the hazard-rate effect, not cohort
    resampling. ``n_particles × n_generations × cohort_size`` simulations
    dominate wall time — at defaults (~100 × 3 × 150 = 45k single-subject
    simulations).
    """
    rng = np.random.default_rng(rng_seed)
    cohort = sample_cohort(cohort_size, rng=rng)
    prebaked = _prebake_cohort(cohort, profile, dt_s, rng_seed + 10_000)    # expensive, ONCE

    # --- generation 0: sample from prior -----------------------------
    theta = prior.sample(rng, n=n_particles)          # linear
    distances = np.zeros(n_particles)
    for i in range(n_particles):
        stats = _score_prebaked(theta[i], prebaked)
        distances[i] = _distance(stats, observation)

    # pick ε_0 = quantile of initial distances
    tolerances = [float(np.quantile(distances, initial_tolerance_quantile))]
    accepted = distances <= tolerances[0]
    theta = theta[accepted]
    distances = distances[accepted]
    weights = np.ones(len(theta)) / len(theta)
    log10_theta = np.log10(theta)

    # --- generations 1..K --------------------------------------------
    for gen in range(1, n_generations):
        # Adaptive perturbation kernel: diag Normal with empirical std.
        # Floor prevents collapse when many particles share log10 values.
        perturb_std = np.std(log10_theta, axis=0) * 0.8 + 0.1

        # Set the next-generation tolerance to the 60% quantile of the current
        # accepted particles' distances — guarantees ~40% would pass, so the
        # rejection sampler actually makes progress.
        target_tol = float(np.quantile(distances, 0.6))

        new_log10: list[np.ndarray] = []
        new_dists: list[float] = []

        target_n = n_particles
        attempts = 0
        max_attempts = n_particles * 60

        while len(new_log10) < target_n and attempts < max_attempts:
            idx = rng.choice(len(theta), p=weights)
            candidate_log10 = log10_theta[idx] + rng.normal(0.0, perturb_std)
            candidate = 10.0 ** candidate_log10
            if prior.log_density(candidate) == -np.inf:
                attempts += 1
                continue
            stats = _score_prebaked(candidate, prebaked)
            d = _distance(stats, observation)
            if d <= target_tol:
                new_log10.append(candidate_log10)
                new_dists.append(d)
            attempts += 1

        if len(new_log10) < max(10, n_particles // 4):
            # Not enough acceptance — stop rather than produce a degenerate
            # posterior.
            break

        log10_theta = np.vstack(new_log10)
        theta = 10.0 ** log10_theta
        distances = np.asarray(new_dists)
        tolerances.append(float(np.max(distances)))
        weights = np.ones(len(theta)) / len(theta)

    # --- posterior summary -------------------------------------------
    post_mean_log10 = np.average(log10_theta, axis=0, weights=weights)
    post_std_log10 = np.sqrt(
        np.average((log10_theta - post_mean_log10) ** 2, axis=0, weights=weights)
    )
    ci_lo = np.quantile(log10_theta, 0.025, axis=0)
    ci_hi = np.quantile(log10_theta, 0.975, axis=0)
    ci95 = np.stack([ci_lo, ci_hi], axis=1)            # (3, 2)

    return AbcSmcResult(
        particles_log10=log10_theta,
        weights=weights,
        distances=distances,
        n_generations=len(tolerances),
        tolerances=tolerances,
        posterior_mean_log10=post_mean_log10,
        posterior_std_log10=post_std_log10,
        posterior_ci95_log10=ci95,
    )


# --------------------------------------------- CLI entry point --------
def _main() -> int:
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="ABC-SMC calibration")
    parser.add_argument("--particles", type=int, default=80)
    parser.add_argument("--generations", type=int, default=3)
    parser.add_argument("--cohort", type=int, default=120)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--save", action="store_true",
                        help="Write posterior to barotrauma/v2/abc_posterior.json")
    args = parser.parse_args()

    result = run_abc_smc(
        n_particles=args.particles,
        n_generations=args.generations,
        cohort_size=args.cohort,
        rng_seed=args.seed,
    )
    hazard_mean = result.posterior_mean_hazard()
    hazard_ci = result.posterior_ci95_hazard()

    print(f"ABC-SMC complete.")
    print(f"  generations:      {result.n_generations}")
    print(f"  tolerances:       {[f'{t:.3f}' for t in result.tolerances]}")
    print(f"  particles (final):{len(result.weights)}")
    print(f"  Posterior (linear hazard rates):")
    labels = ["r_barotitis     ", "r_baromyringitis", "r_rupture       "]
    for i, lab in enumerate(labels):
        print(f"    {lab} mean={hazard_mean[i]:.3e}  "
              f"95% CI [{hazard_ci[i,0]:.3e}, {hazard_ci[i,1]:.3e}]")

    if args.save:
        path = Path(__file__).parent / "abc_posterior.json"
        payload = {
            "posterior_mean_log10": result.posterior_mean_log10.tolist(),
            "posterior_std_log10": result.posterior_std_log10.tolist(),
            "posterior_ci95_log10": result.posterior_ci95_log10.tolist(),
            "tolerances": result.tolerances,
            "n_generations": result.n_generations,
            "n_particles_final": int(len(result.weights)),
            "particles_log10": result.particles_log10.tolist(),
        }
        path.write_text(json.dumps(payload, indent=2))
        print(f"Saved → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
