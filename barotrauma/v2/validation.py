"""
barotrauma.v2.validation
========================

External validation of the v2 model against published hypobaric-chamber
MEB cohorts. Each benchmark carries a citation (PMID), a ChamberProfile
matched to the published study, a CohortPriors override matching the
study's inclusion criteria, and a binomial 95% CI around the observed
prevalence. ``validate_against_cohort`` runs a synthetic cohort through
the profile and checks whether the simulated prevalence falls inside the
observed CI.

This is the complement to ``calibration.py`` — calibration fits hazard
constants against the FAC anchor, validation tests the fitted model on
independent cohorts without re-fitting.

Current benchmarks (all Italian AF, pre-screened aircrew):
- Morgagni 2010 (PMID 20824995): 1,241 aircrew, 1.5% overall barotitis.
- Morgagni 2012 (PMID 22764614): 314 aircrew, 2.3% acute barotitis at
  25,000 ft; 9.2% delayed ear pain (the latter is a different outcome —
  not directly comparable to our p_barotitis).
- Landolfi 2009 (PMID 20027855): 335 pilots, 2.4% TEED-graded barotitis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from . import constants as C
from .calibration import CohortPriors, sample_cohort
from .engine import simulate
from .scenarios import ITALIAN_AF_25K, ITALIAN_AF_35K
from .types import ChamberProfile, PatientState


# ------------------------------ benchmark records ---------------------
@dataclass(frozen=True)
class CohortBenchmark:
    """A single external-validation benchmark."""

    name: str
    reference: str                        # human-readable citation
    pmid: str
    n_subjects: int
    observed_prevalence: float            # point estimate
    profile: ChamberProfile
    priors: CohortPriors
    notes: str = ""

    def binomial_95_ci(self) -> tuple[float, float]:
        """Wilson 95% CI for the observed proportion."""
        return _wilson_ci(self.observed_prevalence, self.n_subjects)


# Pre-screened aircrew priors: Italian AF pre-chamber screening bars active
# URI and filters ETD by tympanometry. The residual recent-URI fraction is
# therefore a transfer prior for resolving/asymptomatic cases, not a general
# population prevalence.
ITALIAN_AF_PRESCREENED = CohortPriors(
    uri_none=1.0 - 0.02,                        # active URI excluded; ~2% recent
    uri_day_1_3=0.0,
    uri_day_4_7=0.0,
    uri_day_8_14=0.02 * 0.5,
    uri_day_15_21=0.02 * 0.3,
    uri_day_22_28=0.02 * 0.2,
    ar_prev=0.10,                                # lower than general pop
    crs_prev=0.015,
    pet_prev=0.005,
    etd_mild_prev=0.04,                          # tympanometry-screened
    etd_moderate_prev=0.008,
    etd_severe_prev=0.0005,
)


MORGAGNI_2010 = CohortBenchmark(
    name="Morgagni 2010 — Italian AF pre-chamber ENT screening",
    reference="Morgagni F et al. 2010, Aviat Space Environ Med",
    pmid="20824995",
    n_subjects=1241,
    observed_prevalence=0.015,                   # 1.5% overall
    profile=ITALIAN_AF_25K,
    priors=ITALIAN_AF_PRESCREENED,
    notes="Overall 1.5% (1.1% screened vs 2.7% controls).",
)

MORGAGNI_2012_25K = CohortBenchmark(
    name="Morgagni 2012 — Italian AF 25,000 ft acute barotitis",
    reference="Morgagni F et al. 2012, Aviat Space Environ Med 83(6):594",
    pmid="22764614",
    n_subjects=314,
    observed_prevalence=0.023,                   # 2.3% acute barotitis
    profile=ITALIAN_AF_25K,
    priors=ITALIAN_AF_PRESCREENED,
    notes="Acute barotitis 2.3%; delayed ear pain 9.2% (different outcome).",
)

LANDOLFI_2009 = CohortBenchmark(
    name="Landolfi 2009 — Italian AF TEED-graded barotitis",
    reference="Landolfi A et al. 2009, Aviat Space Environ Med",
    pmid="20027855",
    n_subjects=335,
    observed_prevalence=0.024,                   # 2.4% TEED-graded
    profile=ITALIAN_AF_25K,
    priors=ITALIAN_AF_PRESCREENED,
    notes="Pre-chamber tympanometry-screened.",
)


BENCHMARKS: dict[str, CohortBenchmark] = {
    "morgagni_2010": MORGAGNI_2010,
    "morgagni_2012_25k": MORGAGNI_2012_25K,
    "landolfi_2009": LANDOLFI_2009,
}


# ---------------------------------- validation runner -----------------
@dataclass
class ValidationResult:
    benchmark: CohortBenchmark
    simulated_prevalence: float
    simulated_n: int
    ci95_observed: tuple[float, float]
    in_ci: bool
    deviation: float
    subgroup_means: dict[str, float] = field(default_factory=dict)


def validate_against_cohort(
    benchmark: CohortBenchmark,
    n_simulated: int = 300,
    dt_s: float = 0.2,
    rng_seed: int = 2026,
) -> ValidationResult:
    """
    Run a synthetic cohort through the benchmark profile and test whether
    the simulated prevalence falls inside the observed 95% CI.
    """
    rng = np.random.default_rng(rng_seed)
    cohort = sample_cohort(n_simulated, rng=rng, priors=benchmark.priors)
    probs = np.fromiter(
        (
            simulate(
                p,
                benchmark.profile,
                dt_s=dt_s,
                rng_seed=rng_seed + i,
            ).risk.p_barotitis
            for i, p in enumerate(cohort)
        ),
        dtype=np.float64,
    )
    simulated_prev = float(np.mean(probs))
    lo, hi = benchmark.binomial_95_ci()
    in_ci = lo <= simulated_prev <= hi
    deviation = simulated_prev - benchmark.observed_prevalence

    # URI subgroup means for clinical sanity
    subgroup: dict[str, list[float]] = {}
    for pat, pr in zip(cohort, probs):
        subgroup.setdefault(pat.uri, []).append(float(pr))
    means = {k: float(np.mean(v)) for k, v in subgroup.items()}

    return ValidationResult(
        benchmark=benchmark,
        simulated_prevalence=simulated_prev,
        simulated_n=n_simulated,
        ci95_observed=(lo, hi),
        in_ci=in_ci,
        deviation=deviation,
        subgroup_means=means,
    )


def validate_all(
    n_simulated: int = 300,
    dt_s: float = 0.2,
    rng_seed: int = 2026,
) -> list[ValidationResult]:
    """Validate against every registered benchmark."""
    return [
        validate_against_cohort(b, n_simulated=n_simulated, dt_s=dt_s,
                                 rng_seed=rng_seed)
        for b in BENCHMARKS.values()
    ]


# ------------------------------------------------ statistics ----------
def _wilson_ci(p: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval — more stable than normal approximation at
    low prevalence."""
    if n <= 0:
        return 0.0, 1.0
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    width = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return max(0.0, centre - width), min(1.0, centre + width)


# ----------------------------------------- CLI runner -----------------
def _main() -> int:
    results = validate_all()
    print("External validation — Italian AF cohorts")
    print("=" * 76)
    for r in results:
        b = r.benchmark
        print(f"\n{b.name}")
        print(f"  Reference: {b.reference} (PMID {b.pmid})")
        print(f"  Observed:  {b.observed_prevalence:.3%} (n={b.n_subjects}, "
              f"95% CI {r.ci95_observed[0]:.3%}-{r.ci95_observed[1]:.3%})")
        print(f"  Simulated: {r.simulated_prevalence:.3%} (n={r.simulated_n})")
        status = "PASS (in CI)" if r.in_ci else "FAIL (outside CI)"
        print(f"  Deviation: {r.deviation:+.3%}   {status}")
        print(f"  URI subgroup means:")
        for k in sorted(r.subgroup_means):
            print(f"    {k:<12s} {r.subgroup_means[k]:.3%}")
    print()
    passing = sum(1 for r in results if r.in_ci)
    print(f"{passing}/{len(results)} benchmarks within the observed 95% CI")
    return 0 if passing == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(_main())
