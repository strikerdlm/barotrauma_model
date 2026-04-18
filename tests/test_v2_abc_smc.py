"""
ABC-SMC sampler tests. Uses small particle / cohort sizes for CI speed.
"""

from __future__ import annotations

import numpy as np
import pytest

from barotrauma.v2.abc_smc import (
    AbcObservation,
    AbcSmcResult,
    HazardPrior,
    run_abc_smc,
)


def test_prior_sampling_and_bounds():
    prior = HazardPrior()
    rng = np.random.default_rng(0)
    theta = prior.sample(rng, n=50)
    assert theta.shape == (50, 3)
    # All values within log10 bounds, linear space
    assert np.all(theta[:, 0] >= 10 ** prior.r_baro_log10[0])
    assert np.all(theta[:, 0] <= 10 ** prior.r_baro_log10[1])


def test_prior_log_density_rejects_out_of_range():
    prior = HazardPrior()
    # Below lower bound
    assert prior.log_density(np.array([1e-20, 1e-15, 1e-20])) == -np.inf
    # Above upper bound
    assert prior.log_density(np.array([1.0, 1.0, 1.0])) == -np.inf
    # In range (log-uniform has finite log density)
    theta = 10.0 ** np.array([-8.0, -9.5, -11.0])
    ld = prior.log_density(theta)
    assert np.isfinite(ld)


def test_abc_smc_produces_posterior_with_ci():
    """Small SMC run — should give a sensible r_baro posterior."""
    result = run_abc_smc(
        n_particles=30,
        n_generations=2,
        cohort_size=40,
        dt_s=0.5,
        rng_seed=2026,
    )
    assert isinstance(result, AbcSmcResult)
    assert result.n_generations >= 1

    mean_hazard = result.posterior_mean_hazard()
    ci = result.posterior_ci95_hazard()

    # r_baro posterior should be near the bisection value (4e-8) within an order of magnitude
    r_baro = mean_hazard[0]
    assert 1e-9 < r_baro < 1e-6, f"r_baro mean outside plausible range: {r_baro}"

    # CI should be a strict interval
    for i in range(3):
        lo, hi = ci[i]
        assert lo < hi


def test_abc_smc_tolerance_decreases_with_generations():
    """Later generations should have tighter (smaller) tolerances."""
    result = run_abc_smc(
        n_particles=30,
        n_generations=3,
        cohort_size=40,
        dt_s=0.5,
        rng_seed=7,
    )
    if result.n_generations >= 2:
        # Non-increasing tolerance schedule
        for i in range(1, len(result.tolerances)):
            assert result.tolerances[i] <= result.tolerances[i - 1] + 1e-6


def test_abc_observation_targets_plausible():
    obs = AbcObservation()
    assert 0.0 < obs.mean_p_barotitis < 0.1
    assert obs.uri_gradient > 1.0
    assert obs.severity_gradient > 1.0
    assert obs.sigma_prev > 0
