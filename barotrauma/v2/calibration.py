"""
barotrauma.v2.calibration
=========================

Population-level calibration of the hazard-rate constants to observed MEB
prevalence. Anchor cohort: Colombian Aerospace Force (FAC), 10-year chamber
training registry, ~5.8% per-individual career MEB prevalence. URI and ET
dysfunction reported as the dominant risk factors.

CLI usage::

    python -m barotrauma.v2.calibration       # run default calibration
    python -m barotrauma.v2.calibration --save # persist constants to JSON


The per-individual career rate (5.8%) is consistent with a ~2% per-exposure
rate across ~3 career chamber exposures — which matches Italian AF
per-exposure rates of 1.5–2.5% in pre-screened aircrew (Morgagni 2010/2012;
Landolfi 2009). See docs/research_notes/04.

Calibration approach
--------------------
1. Draw a synthetic cohort from FAC-like priors (anatomy, ET severity,
   URI-state prevalence, chronic rhinitis, PET).
2. Simulate each subject through a reference chamber profile (default
   FAC_BOGOTA_DEFAULT).
3. Tune the barotitis hazard-rate constant ``HAZARD_BAROTITIS_R`` by scalar
   bisection so that the population mean of ``p_barotitis`` matches the
   target prevalence.
4. Verify that URI is the dominant risk factor in the fitted cohort (i.e.
   URI-positive subjects have a higher mean p_barotitis than URI-negative).

The baromyringitis and rupture rate constants are not independently
calibrated (no FAC severity distribution is available); they are scaled
from the barotitis constant using the literature ratio of Teed-III+ to
Teed-I+ events (~15% of chamber barotitis events, Landolfi 2009).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from . import constants as C
from .anatomy import apply_severity_to_et, sample_population_anatomy
from .scenarios import FAC_BOGOTA_DEFAULT
from .types import (
    ChamberProfile,
    EtFunction,
    EtSeverity,
    PatientAnatomy,
    PatientState,
    UriState,
)


# ------------------------------------------ population-draw priors -----
@dataclass(frozen=True)
class CohortPriors:
    """Population composition priors for the FAC trainee cohort."""

    uri_none: float = 1.0 - (
        C.FAC_URI_ACTIVE_PREVALENCE + C.FAC_URI_RECENT_PREVALENCE
    )
    uri_day_1_3: float = C.FAC_URI_ACTIVE_PREVALENCE * 0.5
    uri_day_4_7: float = C.FAC_URI_ACTIVE_PREVALENCE * 0.5
    uri_day_8_14: float = C.FAC_URI_RECENT_PREVALENCE * 0.5
    uri_day_15_21: float = C.FAC_URI_RECENT_PREVALENCE * 0.3
    uri_day_22_28: float = C.FAC_URI_RECENT_PREVALENCE * 0.2

    ar_prev: float = C.FAC_AR_PREVALENCE
    crs_prev: float = C.FAC_CRS_PREVALENCE
    pet_prev: float = C.FAC_PET_PREVALENCE

    etd_mild_prev: float = C.FAC_ETD_MILD_PREVALENCE
    etd_moderate_prev: float = C.FAC_ETD_MODERATE_PREVALENCE
    etd_severe_prev: float = C.FAC_ETD_SEVERE_PREVALENCE


def sample_cohort(
    n: int,
    rng: np.random.Generator | None = None,
    priors: CohortPriors | None = None,
) -> list[PatientState]:
    """Draw ``n`` synthetic patients from the cohort priors."""
    rng = rng or np.random.default_rng(42)
    priors = priors or CohortPriors()

    anatomies = sample_population_anatomy(rng, n)

    # URI multinomial
    uri_weights = np.array([
        priors.uri_none,
        priors.uri_day_1_3,
        priors.uri_day_4_7,
        priors.uri_day_8_14,
        priors.uri_day_15_21,
        priors.uri_day_22_28,
    ])
    uri_weights = uri_weights / uri_weights.sum()
    uri_labels: list[UriState] = ["none", "day_1_3", "day_4_7", "day_8_14", "day_15_21", "day_22_28"]
    uri_draws = rng.choice(len(uri_labels), size=n, p=uri_weights)

    # Severity multinomial
    sev_weights = np.array([
        1.0 - priors.etd_mild_prev - priors.etd_moderate_prev - priors.etd_severe_prev,
        priors.etd_mild_prev,
        priors.etd_moderate_prev,
        priors.etd_severe_prev,
    ])
    sev_weights = sev_weights / sev_weights.sum()
    sev_labels: list[EtSeverity] = ["normal", "mild", "moderate", "severe"]
    sev_draws = rng.choice(len(sev_labels), size=n, p=sev_weights)

    # PET, AR, CRS
    pet_draws = rng.random(n) < priors.pet_prev
    ar_draws = rng.random(n) < priors.ar_prev
    crs_draws = rng.random(n) < priors.crs_prev

    cohort: list[PatientState] = []
    for i in range(n):
        rhinitis = "chronic_rhinosinusitis" if crs_draws[i] else ("allergic" if ar_draws[i] else "none")
        cohort.append(
            PatientState(
                anatomy=anatomies[i],
                et=EtFunction(severity=sev_labels[sev_draws[i]]),
                uri=uri_labels[uri_draws[i]],
                pet="s1" if pet_draws[i] else "normal",
                rhinitis=rhinitis,  # type: ignore[arg-type]
            )
        )
    return cohort


# ------------------------------------------ prevalence estimator -----
def cohort_mean_p_barotitis(
    cohort: list[PatientState],
    profile: ChamberProfile,
    dt_s: float = 0.2,
    rng_seed: int = 2026,
) -> float:
    """Mean predicted per-exposure p_barotitis across the cohort."""
    from .engine import simulate

    probs = np.fromiter(
        (
            simulate(p, profile, dt_s=dt_s, rng_seed=rng_seed + i).risk.p_barotitis
            for i, p in enumerate(cohort)
        ),
        dtype=np.float64,
    )
    return float(np.mean(probs))


@dataclass
class CalibrationResult:
    target_prevalence: float
    achieved_prevalence: float
    iterations: int
    hazard_barotitis_r: float
    hazard_baromyringitis_r: float
    hazard_rupture_r: float
    per_exposure_to_career_scale: float
    cohort_summary: dict = field(default_factory=dict)


# ----------------------------------------- bisection calibrator ------
def calibrate_hazard_constants(
    target_per_exposure_prevalence: float = 0.02,   # Italian AF mid-range
    n_cohort: int = 300,
    profile: ChamberProfile = FAC_BOGOTA_DEFAULT,
    tol: float = 0.002,
    max_iter: int = 15,
    rng_seed: int = 1337,
    apply_globally: bool = False,
    dt_s: float = 0.2,
) -> CalibrationResult:
    """
    Tune ``HAZARD_BAROTITIS_R`` by bisection so the cohort mean p_barotitis
    matches ``target_per_exposure_prevalence``. The baromyringitis and rupture
    rates are rescaled in proportion.

    If ``apply_globally`` is True, the module-level constants in
    ``barotrauma.v2.constants`` are patched in-place so subsequent ``simulate``
    calls use the calibrated values. This is convenient for scripts but
    side-effectful — prefer the returned ``CalibrationResult`` and explicit
    injection in production code.
    """
    rng = np.random.default_rng(rng_seed)
    cohort = sample_cohort(n_cohort, rng=rng)

    # Remember original
    r_baro_orig = C.HAZARD_BAROTITIS_R
    r_bmrg_orig = C.HAZARD_BAROMYRINGITIS_R
    r_rupt_orig = C.HAZARD_RUPTURE_R
    r_bmrg_ratio = r_bmrg_orig / r_baro_orig
    r_rupt_ratio = r_rupt_orig / r_baro_orig

    lo, hi = 1.0e-10, 5.0e-3
    achieved = float("nan")
    iters = 0

    for iters in range(1, max_iter + 1):
        mid = np.sqrt(lo * hi)       # geometric midpoint (log-space bisection)
        # Inject mid into constants (side-effectful for the duration of this loop)
        C.HAZARD_BAROTITIS_R = float(mid)
        C.HAZARD_BAROMYRINGITIS_R = float(mid * r_bmrg_ratio)
        C.HAZARD_RUPTURE_R = float(mid * r_rupt_ratio)

        achieved = cohort_mean_p_barotitis(
            cohort, profile, dt_s=dt_s, rng_seed=rng_seed + 10_000
        )
        if abs(achieved - target_per_exposure_prevalence) < tol:
            break
        if achieved < target_per_exposure_prevalence:
            lo = mid
        else:
            hi = mid

    # Save calibrated values
    r_baro_cal = C.HAZARD_BAROTITIS_R
    r_bmrg_cal = C.HAZARD_BAROMYRINGITIS_R
    r_rupt_cal = C.HAZARD_RUPTURE_R

    # Compute subgroup summary WHILE calibrated constants are active so
    # the reported per-group means reflect the fitted model.
    from .engine import simulate
    uri_probs: dict[str, list[float]] = {}
    severity_probs: dict[str, list[float]] = {}
    for i, p in enumerate(cohort):
        pb = simulate(p, profile, dt_s=dt_s, rng_seed=rng_seed + 20_000 + i).risk.p_barotitis
        uri_probs.setdefault(p.uri, []).append(pb)
        severity_probs.setdefault(p.et.severity, []).append(pb)

    if not apply_globally:
        # restore originals after summary
        C.HAZARD_BAROTITIS_R = r_baro_orig
        C.HAZARD_BAROMYRINGITIS_R = r_bmrg_orig
        C.HAZARD_RUPTURE_R = r_rupt_orig

    # Convert per-exposure → ~career (5.8% at 3 exposures assumption)
    per_exp_to_career = 1.0 - (1.0 - achieved) ** 3
    summary = {
        "n_cohort": n_cohort,
        "per_exposure_achieved": achieved,
        "per_exposure_target": target_per_exposure_prevalence,
        "career_3_exposures_projected": per_exp_to_career,
        "uri_subgroup_means": {k: float(np.mean(v)) for k, v in uri_probs.items()},
        "severity_subgroup_means": {k: float(np.mean(v)) for k, v in severity_probs.items()},
    }

    return CalibrationResult(
        target_prevalence=target_per_exposure_prevalence,
        achieved_prevalence=float(achieved),
        iterations=iters,
        hazard_barotitis_r=float(r_baro_cal),
        hazard_baromyringitis_r=float(r_bmrg_cal),
        hazard_rupture_r=float(r_rupt_cal),
        per_exposure_to_career_scale=float(per_exp_to_career),
        cohort_summary=summary,
    )


# ---------------------------------------- simple CLI-oriented runner ---
def run_default_calibration() -> CalibrationResult:
    """Run calibration with defaults matching the FAC anchor (5.8%/10 yr)."""
    return calibrate_hazard_constants(
        target_per_exposure_prevalence=0.020,    # per-exposure
        n_cohort=250,
        profile=FAC_BOGOTA_DEFAULT,
        tol=0.0025,
        max_iter=15,
        rng_seed=2026,
        apply_globally=False,
    )


# ----------------------------------------- persistence ---------------
CALIBRATION_FILE = Path(__file__).parent / "calibrated.json"


def save_calibration(result: CalibrationResult, path: Path | str = CALIBRATION_FILE) -> Path:
    """
    Persist calibration results to JSON. ``constants.py`` auto-loads this file
    on import when present, overriding the placeholder hazard rates.
    """
    path = Path(path)
    payload = {
        "meta": {
            "target_per_exposure": result.target_prevalence,
            "achieved_per_exposure": result.achieved_prevalence,
            "iterations": result.iterations,
            "career_projection_3_exposures": result.per_exposure_to_career_scale,
            "fac_career_anchor": C.FAC_TARGET_MEB_PREVALENCE,
        },
        "hazard": {
            "barotitis_r": result.hazard_barotitis_r,
            "baromyringitis_r": result.hazard_baromyringitis_r,
            "rupture_r": result.hazard_rupture_r,
        },
        "cohort_summary": result.cohort_summary,
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def load_calibration(path: Path | str = CALIBRATION_FILE) -> dict | None:
    """Load persisted calibration or return None if absent/invalid."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def apply_calibrated_constants(payload: dict | None = None) -> bool:
    """Patch module-level hazard constants from a calibration payload."""
    payload = payload if payload is not None else load_calibration()
    if payload is None or "hazard" not in payload:
        return False
    h = payload["hazard"]
    C.HAZARD_BAROTITIS_R = float(h["barotitis_r"])
    C.HAZARD_BAROMYRINGITIS_R = float(h["baromyringitis_r"])
    C.HAZARD_RUPTURE_R = float(h["rupture_r"])
    return True


# ------------------------------------------ CLI entry point ---------
def _main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Calibrate v2 hazard constants.")
    parser.add_argument("--target", type=float, default=0.020,
                        help="Target per-exposure MEB prevalence (default 0.020)")
    parser.add_argument("--n", type=int, default=300,
                        help="Cohort size for calibration (default 300)")
    parser.add_argument("--seed", type=int, default=2026,
                        help="RNG seed (default 2026)")
    parser.add_argument("--save", action="store_true",
                        help="Persist result to barotrauma/v2/calibrated.json")
    args = parser.parse_args(argv)

    res = calibrate_hazard_constants(
        target_per_exposure_prevalence=args.target,
        n_cohort=args.n,
        rng_seed=args.seed,
        apply_globally=args.save,
    )
    print("Calibration complete.")
    print(f"  iterations:               {res.iterations}")
    print(f"  target per-exposure:      {res.target_prevalence:.4f}")
    print(f"  achieved per-exposure:    {res.achieved_prevalence:.4f}")
    print(f"  projected career (3×):    {res.per_exposure_to_career_scale:.4f}")
    print(f"  HAZARD_BAROTITIS_R:       {res.hazard_barotitis_r:.4e}")
    print(f"  HAZARD_BAROMYRINGITIS_R:  {res.hazard_baromyringitis_r:.4e}")
    print(f"  HAZARD_RUPTURE_R:         {res.hazard_rupture_r:.4e}")
    print("URI subgroup means:")
    for k, v in sorted(res.cohort_summary["uri_subgroup_means"].items()):
        print(f"  {k:<12s} {v:.4f}")
    print("Severity subgroup means:")
    for k, v in sorted(res.cohort_summary["severity_subgroup_means"].items()):
        print(f"  {k:<12s} {v:.4f}")
    if args.save:
        path = save_calibration(res)
        print(f"Saved calibration → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
