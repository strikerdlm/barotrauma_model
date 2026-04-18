"""
Visual-regression-style pinned-baseline test against the Groth 1986
pressure-chamber trajectory used by Kanick & Doyle 2005 as their Fig 3
validation reference.

The fixture (``tests/fixtures/kanick_doyle_2005_fig3.json``) was recorded
from a healthy baseline PatientState on GROTH_1986_VALIDATION with dt=0.1 s
and a fixed RNG seed. The test asserts that future runs stay within
tight tolerances on ΔP at every sampled time point, plus on the summary
metrics (max |ΔP|, p_barotitis). Any physics change that shifts the
Kanick-Doyle-matched trajectory will fail this test loudly.

How to regenerate the fixture (requires model-behaviour change review)::

    python -c "
    import json, numpy as np
    from pathlib import Path
    from barotrauma.v2 import simulate, PatientState
    from barotrauma.v2.scenarios import GROTH_1986_VALIDATION
    r = simulate(PatientState(), GROTH_1986_VALIDATION, dt_s=0.1, rng_seed=2026)
    t = r.trace.t_s; dp = r.trace.delta_p_mmHg
    sample_ts = [0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,79]
    samples = [{'t_s': float(t[np.argmin(abs(t-st))]),
                'altitude_ft': float(r.trace.altitude_ft[np.argmin(abs(t-st))]),
                'p_ambient_mmHg': float(r.trace.p_ambient_mmHg[np.argmin(abs(t-st))]),
                'delta_p_mmHg': float(dp[np.argmin(abs(t-st))])}
               for st in sample_ts]
    Path('tests/fixtures/kanick_doyle_2005_fig3.json').write_text(json.dumps({
        'profile': 'GROTH_1986_VALIDATION',
        'patient': 'PatientState() — healthy baseline',
        'rng_seed': 2026, 'dt_s': 0.1,
        'max_abs_delta_p_mmHg': float(r.risk.max_abs_delta_p_mmHg),
        'p_barotitis': float(r.risk.p_barotitis),
        'risk_category': r.risk.risk_category(),
        'samples': samples,
    }, indent=2))
    "

Only regenerate when you deliberately change the physics core and the
delta is reviewed.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from barotrauma.v2 import simulate, PatientState
from barotrauma.v2.scenarios import GROTH_1986_VALIDATION


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "kanick_doyle_2005_fig3.json"


@pytest.fixture(scope="module")
def fixture() -> dict:
    assert FIXTURE_PATH.exists(), f"fixture missing: {FIXTURE_PATH}"
    return json.loads(FIXTURE_PATH.read_text())


@pytest.fixture(scope="module")
def live_result(fixture):
    # Reproduce the recorded conditions
    return simulate(
        PatientState(),
        GROTH_1986_VALIDATION,
        dt_s=fixture["dt_s"],
        rng_seed=fixture["rng_seed"],
    )


def test_fixture_contents_are_valid(fixture):
    assert fixture["profile"] == "GROTH_1986_VALIDATION"
    assert fixture["dt_s"] > 0
    assert fixture["max_abs_delta_p_mmHg"] >= 0
    assert 0.0 <= fixture["p_barotitis"] <= 1.0
    assert len(fixture["samples"]) > 5


def test_max_abs_delta_p_within_tolerance(fixture, live_result):
    """Peak |ΔP| should stay within ±5% or ±2 mmHg (whichever larger)."""
    expected = fixture["max_abs_delta_p_mmHg"]
    actual = live_result.risk.max_abs_delta_p_mmHg
    tolerance = max(0.05 * expected, 2.0)
    assert abs(actual - expected) < tolerance, (
        f"peak |ΔP| drift: expected {expected:.2f}, got {actual:.2f} "
        f"(tolerance ±{tolerance:.2f})"
    )


def test_p_barotitis_matches(fixture, live_result):
    """Per-exposure p_barotitis should be near-identical (±0.5pp)."""
    expected = fixture["p_barotitis"]
    actual = live_result.risk.p_barotitis
    assert abs(actual - expected) < 0.005, (
        f"p_barotitis drift: expected {expected:.4f}, got {actual:.4f}"
    )


def test_risk_category_stable(fixture, live_result):
    assert live_result.risk.risk_category() == fixture["risk_category"]


def test_sampled_delta_p_trajectory_within_tolerance(fixture, live_result):
    """
    For every recorded sample timestamp, the live ΔP should match the
    fixture ΔP within ±5% or ±1 mmHg (whichever larger).
    """
    t = live_result.trace.t_s
    dp = live_result.trace.delta_p_mmHg
    mismatches = []
    for sample in fixture["samples"]:
        st = sample["t_s"]
        expected_dp = sample["delta_p_mmHg"]
        idx = int(np.argmin(np.abs(t - st)))
        actual_dp = float(dp[idx])
        tolerance = max(0.05 * abs(expected_dp), 1.0)
        if abs(actual_dp - expected_dp) > tolerance:
            mismatches.append(
                f"t={st:.1f}s: expected ΔP={expected_dp:+.2f}, "
                f"got {actual_dp:+.2f} (tol ±{tolerance:.2f})"
            )
    assert not mismatches, (
        "Kanick-Doyle Fig 3 trajectory drift detected:\n  "
        + "\n  ".join(mismatches)
    )


def test_sampled_altitude_and_ambient_pressure_consistent(fixture, live_result):
    """
    Profile altitude and atmospheric pressure are fully deterministic — any
    drift here would indicate a scenarios.py or atmosphere.py regression.
    """
    t = live_result.trace.t_s
    alt = live_result.trace.altitude_ft
    p = live_result.trace.p_ambient_mmHg
    for sample in fixture["samples"]:
        st = sample["t_s"]
        idx = int(np.argmin(np.abs(t - st)))
        assert abs(float(alt[idx]) - sample["altitude_ft"]) < 5.0
        assert abs(float(p[idx]) - sample["p_ambient_mmHg"]) < 0.5
