"""Tests for barotrauma.v2.career — multi-exposure career modeling."""

from __future__ import annotations

import math

import pytest

from barotrauma.v2 import (
    CareerCohortResult,
    CareerExposure,
    CareerResult,
    PatientAnatomy,
    PatientState,
    simulate,
    simulate_career,
    simulate_career_cohort,
)
from barotrauma.v2.career import _career_probability
from barotrauma.v2.scenarios import FAC_BOGOTA_DEFAULT


def test_career_probability_identity_zero():
    """All-zero inputs give zero career probability."""
    assert _career_probability([0.0, 0.0, 0.0]) == 0.0


def test_career_probability_identity_one():
    """Any single p=1.0 gives career probability 1.0."""
    assert _career_probability([0.0, 1.0, 0.3]) == pytest.approx(1.0)


def test_career_probability_matches_closed_form():
    """For identical per-exposure p, career_p == 1 − (1 − p)ⁿ."""
    p = 0.02
    n = 3
    expected = 1.0 - (1.0 - p) ** n
    got = _career_probability([p] * n)
    assert got == pytest.approx(expected)


def test_career_probability_rejects_out_of_range():
    with pytest.raises(ValueError):
        _career_probability([0.1, -0.05, 0.2])
    with pytest.raises(ValueError):
        _career_probability([1.1])


def test_simulate_career_requires_exposures():
    with pytest.raises(ValueError):
        simulate_career([])


def test_simulate_career_single_exposure_equals_simulate():
    """Career probability with one exposure equals the single-exposure
    p_barotitis identically when the same rng_seed is used."""
    patient = PatientState(uri="none")
    single = simulate(patient, FAC_BOGOTA_DEFAULT, rng_seed=42)
    career = simulate_career(
        [CareerExposure(patient, FAC_BOGOTA_DEFAULT, rng_seed=42)]
    )
    assert career.p_career_barotitis == pytest.approx(single.risk.p_barotitis)
    assert career.n_exposures == 1
    assert len(career.per_exposure_results) == 1


def test_simulate_career_three_exposures_matches_closed_form():
    """When all 3 exposures use the same rng_seed (deterministic), the
    career probability equals the closed-form 1 − (1 − p)ⁿ."""
    patient = PatientState(uri="none")
    career = simulate_career(
        [CareerExposure(patient, FAC_BOGOTA_DEFAULT, rng_seed=42)
         for _ in range(3)]
    )
    # Per-exposure values are deterministic (same seed) → identical
    ps = career.per_exposure_p_barotitis
    assert ps[0] == pytest.approx(ps[1])
    assert ps[0] == pytest.approx(ps[2])
    expected = 1.0 - (1.0 - ps[0]) ** 3
    assert career.p_career_barotitis == pytest.approx(expected)
    assert career.n_exposures == 3


def test_simulate_career_uri_peak_dominates():
    """A career with a URI day 4–7 exposure should have substantially higher
    career barotitis than a matched career with no URI."""
    healthy_career = simulate_career(
        [CareerExposure(PatientState(uri="none"), FAC_BOGOTA_DEFAULT)
         for _ in range(3)]
    )
    uri_career = simulate_career(
        [
            CareerExposure(PatientState(uri="none"), FAC_BOGOTA_DEFAULT),
            CareerExposure(PatientState(uri="day_4_7"), FAC_BOGOTA_DEFAULT),
            CareerExposure(PatientState(uri="none"), FAC_BOGOTA_DEFAULT),
        ]
    )
    # URI peak exposure ~50–100× healthy baseline; career p should exceed
    # healthy baseline by at least an order of magnitude.
    assert uri_career.p_career_barotitis > 10 * healthy_career.p_career_barotitis


def test_simulate_career_order_invariance():
    """Career probability is invariant to the order of exposures (only the
    set of per-exposure probabilities matters). Tested with deterministic
    seeding so per-exposure p values are reproducible."""
    exposures = [
        CareerExposure(PatientState(uri="none"), FAC_BOGOTA_DEFAULT, rng_seed=1),
        CareerExposure(PatientState(uri="day_4_7"), FAC_BOGOTA_DEFAULT, rng_seed=2),
        CareerExposure(PatientState(uri="day_8_14"), FAC_BOGOTA_DEFAULT, rng_seed=3),
    ]
    a = simulate_career(exposures)
    b = simulate_career(list(reversed(exposures)))
    assert a.p_career_barotitis == pytest.approx(b.p_career_barotitis)
    assert a.p_career_rupture == pytest.approx(b.p_career_rupture)


def test_simulate_career_cohort_basic():
    """Cohort career simulation over 3 subjects × 3 exposures returns well-
    formed results with correlation-aware mean matching the naive identity
    when all subjects are identical (no correlation to exploit).

    Uses deterministic rng_seed per exposure so the per-exposure p values
    are pointwise identical; under that condition the identity holds
    exactly."""
    base = PatientState(uri="none")
    cohort = [
        [CareerExposure(base, FAC_BOGOTA_DEFAULT, rng_seed=42) for _ in range(3)]
        for _ in range(3)
    ]
    res = simulate_career_cohort(cohort)
    assert isinstance(res, CareerCohortResult)
    assert res.n_subjects == 3
    assert res.exposures_per_subject == 3
    # All subjects identical → career mean == naive identity
    assert res.mean_p_career_barotitis == pytest.approx(
        res.naive_indep_p_career_barotitis
    )


def test_simulate_career_cohort_correlation_reduces_career_rate():
    """When subjects differ in anatomy, the population career rate
    ``mean[1 − ∏(1 − p_i)]`` should be LOWER than the naive identity
    ``1 − (1 − mean_p)ⁿ`` because intra-subject repetition concentrates
    risk in high-risk subjects.

    This is Jensen's inequality applied to the convex function
    ``f(p) = 1 − (1 − p)ⁿ``.
    """
    # Two-subject cohort with substantially different risk
    low_risk = PatientState(uri="none", et=PatientState().et)  # base
    # High risk: moderate ETD severity (anatomy + severity are the fixed traits)
    high_risk = PatientState.__class__(
        **{**vars(PatientState()), }
    ) if False else PatientState(uri="none")
    # Use URI as a proxy for per-subject risk trait (fixed across subject's career)
    low_exposures = [CareerExposure(PatientState(uri="none"), FAC_BOGOTA_DEFAULT)
                     for _ in range(3)]
    high_exposures = [CareerExposure(PatientState(uri="day_4_7"), FAC_BOGOTA_DEFAULT)
                      for _ in range(3)]
    cohort = [low_exposures, high_exposures]

    res = simulate_career_cohort(cohort)
    # Jensen's inequality: correlation-aware mean ≤ naive identity
    # (strict when subjects differ)
    assert res.mean_p_career_barotitis <= res.naive_indep_p_career_barotitis + 1e-12
    # And strictly less when subjects differ
    assert res.mean_p_career_barotitis < res.naive_indep_p_career_barotitis


def test_simulate_career_cohort_rejects_mismatched_exposure_count():
    """All subjects in the cohort must have the same number of exposures."""
    base = PatientState(uri="none")
    cohort = [
        [CareerExposure(base, FAC_BOGOTA_DEFAULT)] * 2,
        [CareerExposure(base, FAC_BOGOTA_DEFAULT)] * 3,
    ]
    with pytest.raises(ValueError):
        simulate_career_cohort(cohort)


def test_simulate_career_cohort_rejects_empty_input():
    with pytest.raises(ValueError):
        simulate_career_cohort([])
    with pytest.raises(ValueError):
        simulate_career_cohort([[]])
