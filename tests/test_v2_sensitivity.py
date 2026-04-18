"""
Sobol sensitivity smoke tests. Uses small N for CI speed; production
runs should use N=128+ for stable first-order estimates.
"""

from __future__ import annotations

import numpy as np
import pytest

from barotrauma.v2.sensitivity import (
    DEFAULT_PARAMETERS,
    ParameterSpec,
    SobolResult,
    run_sobol,
)


def test_parameter_spec_validates():
    p = ParameterSpec("test", 10.0, 50.0)
    assert p.low < p.high


def test_default_parameters_are_sensible():
    for ps in DEFAULT_PARAMETERS:
        assert ps.low < ps.high
        assert ps.name.isupper() or "_" in ps.name


def test_sobol_runs_and_returns_result():
    result = run_sobol(n=16, dt_s=0.5, rng_seed=7)
    assert isinstance(result, SobolResult)
    assert len(result.parameter_names) == len(DEFAULT_PARAMETERS)
    assert result.first_order.shape == (len(DEFAULT_PARAMETERS),)
    assert result.total_order.shape == (len(DEFAULT_PARAMETERS),)
    assert result.n_evaluations == (2 + len(DEFAULT_PARAMETERS)) * 16


def test_sobol_aperture_half_dominates():
    """
    The APERTURE_HALF_MMHG parameter should have the largest total-order
    Sobol index among the default set — it controls when the descent-
    aperture collapses, which is the primary driver of p_barotitis.
    """
    result = run_sobol(n=24, dt_s=0.5, rng_seed=7)
    idx_half = result.parameter_names.index("APERTURE_HALF_MMHG")
    # Largest |S_T| across parameters
    dominant_idx = int(np.argmax(np.abs(result.total_order)))
    assert dominant_idx == idx_half, (
        f"expected APERTURE_HALF_MMHG to dominate, got "
        f"{result.parameter_names[dominant_idx]}"
    )


def test_sobol_total_order_nonzero_variance():
    result = run_sobol(n=16, dt_s=0.5, rng_seed=7)
    assert result.variance_total > 0
