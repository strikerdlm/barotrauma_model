"""
barotrauma.v2.career
====================

Multi-exposure career modeling. A chamber trainee flies 2–5 exposures across
a career; each exposure is a draw from the simulator, but the exposures are
NOT independent — the same subject carries the same anatomy, the same base
ET severity, the same chronic rhinitis status, etc.

The one-exposure ``simulate`` function answers "what is p_barotitis for this
patient on this profile?". The ``simulate_career`` function in this module
answers "what is the probability that this subject experiences ≥ 1 barotrauma
event across this full training career?" under the correct
intra-subject-correlated model, rather than under the
independent-across-exposures approximation.

Usage::

    from barotrauma.v2 import PatientState, EtFunction, PatientAnatomy
    from barotrauma.v2.scenarios import FAC_BOGOTA_DEFAULT
    from barotrauma.v2.career import simulate_career, CareerExposure

    base = PatientState(
        anatomy=PatientAnatomy(mastoid_volume_ml=7.0, age_years=28),
        et=EtFunction(severity="mild"),
    )

    exposures = [
        CareerExposure(patient=base.with_uri("none"),
                       profile=FAC_BOGOTA_DEFAULT),
        CareerExposure(patient=base.with_uri("day_4_7"),
                       profile=FAC_BOGOTA_DEFAULT),
        CareerExposure(patient=base.with_uri("none"),
                       profile=FAC_BOGOTA_DEFAULT),
    ]

    res = simulate_career(exposures)
    print(res.p_career_barotitis, res.per_exposure_p_barotitis)

Rationale
---------
The independence approximation ``1 − (1 − p̄)ⁿ`` treats each career exposure
as a fresh Bernoulli trial with identical risk. Under realistic correlations
(fixed anatomy, fixed ET severity), the true career rate is lower than the
independence projection because a low-risk subject systematically draws low
risk across all exposures and a high-risk subject systematically draws high.
The dispersion of per-subject career risks is wider than the Bernoulli
approximation; the mean of ``1 − ∏ᵢ(1 − pᵢ)`` taken over an anatomy cohort
is therefore bounded above by the population-level ``1 − (1 − p̄)ⁿ`` identity.

The module exposes three primitives:

- :class:`CareerExposure` — one (patient, profile) pair representing a single
  chamber run.
- :func:`simulate_career` — per-subject career simulation returning both the
  correlation-aware career probability and the per-exposure trace.
- :func:`simulate_career_cohort` — population-level career simulation across
  a cohort of subjects, returning the mean career probability and its
  distribution moments.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

from .engine import simulate
from .types import (
    ChamberProfile,
    PatientState,
    SimulationResult,
)


@dataclass(frozen=True)
class CareerExposure:
    """One chamber exposure in a trainee's career.

    Attributes
    ----------
    patient : PatientState
        Patient snapshot at the time of this exposure. Acute state (URI,
        medication, previous_meb) may differ between exposures for the same
        subject; anatomy and base ET severity typically do not.
    profile : ChamberProfile
        Chamber profile for this exposure.
    dt_s : float
        Integrator step. Default 0.1 s.
    gas_exchange_full : bool
        Use Doyle 2017 multi-pathway gas exchange. Default False (v2.1
        trans-mucosal only).
    rng_seed : int | None
        Seed for the stochastic swallow-interval jitter on this exposure.
        ``None`` (default) pulls from OS entropy, producing non-deterministic
        per-call outputs; setting a deterministic integer is recommended when
        reproducibility across runs is required (e.g. regression tests or
        publication-anchored calibrations).
    """

    patient: PatientState
    profile: ChamberProfile
    dt_s: float = 0.1
    gas_exchange_full: bool = False
    rng_seed: int | None = None


@dataclass
class CareerResult:
    """Outcome of a single subject's career simulation.

    Attributes
    ----------
    per_exposure_results : list[SimulationResult]
        Full per-exposure simulation output, in the order exposures were
        provided. Index ``i`` corresponds to the ``i``-th career chamber run.
    per_exposure_p_barotitis : list[float]
        Convenience view: per-exposure p_barotitis values.
    per_exposure_p_baromyringitis : list[float]
    per_exposure_p_rupture : list[float]
    p_career_barotitis : float
        1 − ∏ᵢ(1 − pᵢ) for barotitis. This is the correct per-subject
        career probability given the specified exposures; it uses the
        independence of events conditional on the subject's fixed
        parameters, NOT the independence of the subject's parameters from
        each other.
    p_career_baromyringitis : float
    p_career_rupture : float
    n_exposures : int
    """

    per_exposure_results: list[SimulationResult]
    per_exposure_p_barotitis: list[float]
    per_exposure_p_baromyringitis: list[float]
    per_exposure_p_rupture: list[float]
    p_career_barotitis: float
    p_career_baromyringitis: float
    p_career_rupture: float
    n_exposures: int


def _career_probability(probs: Sequence[float]) -> float:
    """Return 1 − ∏(1 − p_i), the probability of ≥ 1 event across exposures
    when per-exposure outcomes are conditionally independent given the
    subject's fixed parameters."""
    survivor = 1.0
    for p in probs:
        if not (0.0 <= p <= 1.0):
            raise ValueError(f"probability out of range: {p}")
        survivor *= 1.0 - p
    return 1.0 - survivor


def simulate_career(exposures: Sequence[CareerExposure]) -> CareerResult:
    """Simulate one trainee's career across a sequence of chamber exposures.

    Each exposure is simulated independently; the career probability is the
    chance of ≥ 1 event across the sequence, which is ``1 − ∏ᵢ(1 − pᵢ)`` for
    each outcome.

    Parameters
    ----------
    exposures : sequence of CareerExposure
        Must be non-empty. Order matters only for reporting; the probability
        calculation is order-independent.

    Returns
    -------
    CareerResult
    """
    if not exposures:
        raise ValueError("simulate_career requires at least one exposure")

    per_ex: list[SimulationResult] = []
    p_baro: list[float] = []
    p_bmrg: list[float] = []
    p_rupt: list[float] = []

    for e in exposures:
        r = simulate(
            e.patient,
            e.profile,
            dt_s=e.dt_s,
            rng_seed=e.rng_seed,
            gas_exchange_full=e.gas_exchange_full,
        )
        per_ex.append(r)
        p_baro.append(float(r.risk.p_barotitis))
        p_bmrg.append(float(r.risk.p_baromyringitis))
        p_rupt.append(float(r.risk.p_rupture))

    return CareerResult(
        per_exposure_results=per_ex,
        per_exposure_p_barotitis=p_baro,
        per_exposure_p_baromyringitis=p_bmrg,
        per_exposure_p_rupture=p_rupt,
        p_career_barotitis=_career_probability(p_baro),
        p_career_baromyringitis=_career_probability(p_bmrg),
        p_career_rupture=_career_probability(p_rupt),
        n_exposures=len(exposures),
    )


@dataclass
class CareerCohortResult:
    """Population-level career result across a cohort of subjects.

    Attributes
    ----------
    n_subjects : int
    exposures_per_subject : int
    mean_p_career_barotitis : float
        Cohort mean of per-subject career probabilities. This is the
        correlation-aware career-rate estimate; compare with the naive
        population-independence identity ``1 − (1 − mean_p_exposure)ⁿ`` to
        quantify the correction.
    mean_p_career_baromyringitis : float
    mean_p_career_rupture : float
    naive_indep_p_career_barotitis : float
        ``1 − (1 − mean_p_exposure_barotitis)ⁿ`` using the cohort mean
        per-exposure probability. This is the identity the FAC cohort paper
        uses; we report it for comparison with the correlation-aware mean.
    per_subject_career_p_barotitis : list[float]
        Full distribution of per-subject career p_barotitis values. Allows
        quantile computation downstream.
    mean_p_exposure_barotitis : float
        Cohort mean of per-exposure p_barotitis (averaged over subjects and
        exposures). Used to compute the naive identity and to verify
        calibration convergence.
    """

    n_subjects: int
    exposures_per_subject: int
    mean_p_career_barotitis: float
    mean_p_career_baromyringitis: float
    mean_p_career_rupture: float
    naive_indep_p_career_barotitis: float
    per_subject_career_p_barotitis: list[float] = field(default_factory=list)
    mean_p_exposure_barotitis: float = 0.0


def simulate_career_cohort(
    cohort_exposures: Sequence[Sequence[CareerExposure]],
) -> CareerCohortResult:
    """Simulate careers across a cohort of subjects.

    Each element of ``cohort_exposures`` is a subject; each element of that
    inner sequence is one chamber exposure in that subject's career. Inner
    sequence lengths MUST be equal across subjects (a single career-exposure
    count is reported in the result).

    Parameters
    ----------
    cohort_exposures : sequence of sequences of CareerExposure
        ``cohort_exposures[i][j]`` is subject ``i``'s ``j``-th exposure.
    """
    if not cohort_exposures:
        raise ValueError("simulate_career_cohort requires at least one subject")
    n_exposures = len(cohort_exposures[0])
    if n_exposures == 0:
        raise ValueError("each subject must have at least one exposure")
    if any(len(s) != n_exposures for s in cohort_exposures):
        raise ValueError(
            "all subjects must have the same number of career exposures"
        )

    per_subj_p_career_baro: list[float] = []
    per_subj_p_career_bmrg: list[float] = []
    per_subj_p_career_rupt: list[float] = []
    all_per_ex_baro: list[float] = []

    for subject_exposures in cohort_exposures:
        r = simulate_career(subject_exposures)
        per_subj_p_career_baro.append(r.p_career_barotitis)
        per_subj_p_career_bmrg.append(r.p_career_baromyringitis)
        per_subj_p_career_rupt.append(r.p_career_rupture)
        all_per_ex_baro.extend(r.per_exposure_p_barotitis)

    mean_p_baro = sum(per_subj_p_career_baro) / len(per_subj_p_career_baro)
    mean_p_bmrg = sum(per_subj_p_career_bmrg) / len(per_subj_p_career_bmrg)
    mean_p_rupt = sum(per_subj_p_career_rupt) / len(per_subj_p_career_rupt)
    mean_p_ex_baro = sum(all_per_ex_baro) / len(all_per_ex_baro)
    naive = 1.0 - (1.0 - mean_p_ex_baro) ** n_exposures

    return CareerCohortResult(
        n_subjects=len(cohort_exposures),
        exposures_per_subject=n_exposures,
        mean_p_career_barotitis=mean_p_baro,
        mean_p_career_baromyringitis=mean_p_bmrg,
        mean_p_career_rupture=mean_p_rupt,
        naive_indep_p_career_barotitis=naive,
        per_subject_career_p_barotitis=per_subj_p_career_baro,
        mean_p_exposure_barotitis=mean_p_ex_baro,
    )
