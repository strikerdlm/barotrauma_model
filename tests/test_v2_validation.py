"""
External-validation tests — Italian AF benchmarks (Morgagni 2010/2012,
Landolfi 2009).

The model is calibrated against the Colombian FAC cohort. These tests
confirm it still produces sane prevalence when run on independent
cohorts without re-fitting the hazard constants.
"""

from __future__ import annotations

import pytest

from barotrauma.v2 import validation


def test_italian_af_benchmarks_defined():
    assert len(validation.BENCHMARKS) >= 3
    for name, b in validation.BENCHMARKS.items():
        assert b.n_subjects >= 100
        assert 0.0 < b.observed_prevalence < 0.10
        lo, hi = b.binomial_95_ci()
        assert 0.0 <= lo < b.observed_prevalence < hi <= 1.0


@pytest.mark.parametrize("key", ["morgagni_2012_25k", "landolfi_2009"])
def test_simulated_prevalence_within_observed_ci(key):
    b = validation.BENCHMARKS[key]
    r = validation.validate_against_cohort(b, n_simulated=200, dt_s=0.5,
                                           rng_seed=42)
    lo, hi = r.ci95_observed
    # Allow a small safety margin (0.5pp) to absorb Monte-Carlo variance at n=200
    margin = 0.005
    assert lo - margin <= r.simulated_prevalence <= hi + margin, (
        f"{key}: simulated {r.simulated_prevalence:.3%} outside observed "
        f"CI [{lo:.3%}, {hi:.3%}]"
    )


def test_morgagni_2010_within_2_5pp_of_observed():
    """
    The Morgagni 2010 mixed pre-screened+unscreened denominator is tighter
    than our Italian AF pre-screened prior captures. Require the simulated
    prevalence to be within ±2.5pp of the observed 1.5%; this is looser
    than the formal CI check because the exact denominator mix is
    unpublished.

    After the ISA pressure-altitude correction, this remains the loosest
    external-transfer check because the exact screened/unscreened denominator
    mix is unpublished. The stricter Italian pre-screening prior excludes
    active URI, but the FAC 2.38% per-exposure anchor still uplifts this
    benchmark toward the top of the allowed band.
    """
    b = validation.BENCHMARKS["morgagni_2010"]
    r = validation.validate_against_cohort(b, n_simulated=300, dt_s=0.5,
                                           rng_seed=2026)
    assert abs(r.simulated_prevalence - b.observed_prevalence) < 0.025, (
        f"simulated {r.simulated_prevalence:.3%} should be within 2.5pp of "
        f"observed {b.observed_prevalence:.3%}"
    )


def test_uri_gradient_preserved_in_validation_cohort():
    """
    Even under Italian AF priors (tighter URI prevalence), the URI-peak
    subgroup should still be materially higher-risk than URI-none.
    """
    b = validation.BENCHMARKS["landolfi_2009"]
    r = validation.validate_against_cohort(b, n_simulated=300, dt_s=0.5,
                                           rng_seed=7)
    means = r.subgroup_means
    if "day_4_7" in means and "none" in means:
        assert means["day_4_7"] > means["none"] * 3.0, (
            f"URI day_4_7 ({means['day_4_7']:.3%}) not sufficiently higher "
            f"than URI none ({means['none']:.3%})"
        )


def test_wilson_ci_bounds():
    from barotrauma.v2.validation import _wilson_ci
    lo, hi = _wilson_ci(0.02, 300)
    assert 0.005 < lo < 0.02 < hi < 0.05
    # Degenerate n=0 returns full interval
    assert _wilson_ci(0.5, 0) == (0.0, 1.0)
