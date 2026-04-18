"""
Risk / hazard-model tests.
"""

from __future__ import annotations

import numpy as np
import pytest

from barotrauma.v2 import (
    FAC_BOGOTA_DEFAULT,
    PatientState,
    RAPID_DESCENT_10K_FT_MIN,
    SLOW_DESCENT_1K_FT_MIN,
    simulate,
)
from barotrauma.v2.risk import (
    cumulative_hazard,
    probability_from_hazard,
    score_with_uncertainty,
)
from barotrauma.v2 import constants as C


def test_probability_zero_when_hazard_zero():
    assert probability_from_hazard(0.0) == pytest.approx(0.0)


def test_probability_approaches_one_for_large_hazard():
    assert probability_from_hazard(50.0) > 0.999


def test_cumulative_hazard_integration_units():
    """Constant ΔP = 50 mmHg above threshold 18.4 for 10 s."""
    n = 100
    dp = np.full(n, 50.0, dtype=np.float64)
    dt_s = 0.1
    excess = 50.0 - 18.4
    h = cumulative_hazard(dp, dt_s, 18.4, 1.0, 1.0)
    assert h == pytest.approx(excess * n * dt_s, rel=0.01)


def test_subthreshold_gives_zero_hazard():
    dp = np.array([10.0, 12.0, 15.0], dtype=np.float64)
    h = cumulative_hazard(dp, 0.1, 18.4, 1.0, 1.0)
    assert h == pytest.approx(0.0, abs=1e-9)


def test_rupture_monotone_with_descent_rate():
    """
    Rupture hazard (cubic on excess) is peak-dominated and must increase
    with descent rate. Barotitis is NOT monotonic — its time-above-threshold
    integral can be larger for a slow-but-long descent.
    """
    p = PatientState()
    slow = simulate(p, SLOW_DESCENT_1K_FT_MIN).risk
    rapid = simulate(p, RAPID_DESCENT_10K_FT_MIN).risk
    assert rapid.p_rupture >= slow.p_rupture
    assert rapid.max_abs_delta_p_mmHg >= slow.max_abs_delta_p_mmHg


def test_recommended_descent_lowers_with_severity():
    healthy = simulate(PatientState(), FAC_BOGOTA_DEFAULT).risk
    from barotrauma.v2.types import EtFunction
    severe = simulate(
        PatientState(et=EtFunction(severity="severe")), FAC_BOGOTA_DEFAULT
    ).risk
    assert severe.recommended_max_descent_ft_min <= healthy.recommended_max_descent_ft_min


def test_uncertainty_ci_envelops_point_estimate():
    trace_result = simulate(PatientState(uri="day_4_7"), FAC_BOGOTA_DEFAULT)
    from barotrauma.v2.pathophysiology import modifiers_for_patient
    m = modifiers_for_patient(trace_result.patient)
    r = score_with_uncertainty(trace_result.trace, trace_result.patient, m,
                               n_mc=200, rng=np.random.default_rng(0))
    assert r.ci95_barotitis is not None
    lo, hi = r.ci95_barotitis
    # Point estimate within the CI (up to MC noise)
    assert lo <= r.p_barotitis <= hi + 1e-6


def test_risk_category_thresholds():
    from barotrauma.v2.types import RiskResult
    r = RiskResult(
        p_barotitis=0.02, p_baromyringitis=0, p_rupture=0,
        max_abs_delta_p_mmHg=10,
        auc_mmHg_s_barotitis=0, auc_mmHg_s_baromyringitis=0,
        dominant_risk_factor="baseline",
        recommended_max_descent_ft_min=10000,
    )
    assert r.risk_category() == "low"
    r2 = RiskResult(**{**r.__dict__, "p_barotitis": 0.25})
    assert r2.risk_category() == "high"
    r3 = RiskResult(**{**r.__dict__, "p_barotitis": 0.8})
    assert r3.risk_category() == "very_high"
