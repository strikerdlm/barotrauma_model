"""Ghadiali FEM muscle-mechanics extension tests."""

from __future__ import annotations

import numpy as np
import pytest

from barotrauma.v2 import (
    FAC_BOGOTA_DEFAULT,
    MuscleMechanics,
    PatientState,
    RAPID_DESCENT_10K_FT_MIN,
    default_dysfunctional_mechanics,
    default_healthy_mechanics,
    simulate,
)
from barotrauma.v2.et_muscle import (
    MuscleState,
    fge_modulation,
    record_swallow,
    update_state,
)


def test_disabled_mechanics_returns_1():
    s = MuscleState()
    m = MuscleMechanics(enabled=False)
    assert fge_modulation(s, 0.0, m) == pytest.approx(1.0)


def test_healthy_mechanics_backward_compat_close_to_v21():
    """Healthy mechanics should produce ΔP close to v2.1 (no-mechanics) run."""
    r_v21 = simulate(PatientState(), FAC_BOGOTA_DEFAULT, rng_seed=42)
    r_v22 = simulate(
        PatientState(), FAC_BOGOTA_DEFAULT,
        muscle_mechanics=default_healthy_mechanics(),
        rng_seed=42,
    )
    # Small differences allowed (priming boost); no catastrophic drift
    delta = abs(r_v22.risk.p_barotitis - r_v21.risk.p_barotitis)
    assert delta < 0.005


def test_adhesion_accumulates_without_swallow():
    """Adhesion should build up monotonically when ET isn't opening."""
    m = default_healthy_mechanics()
    s = MuscleState()
    update_state(s, 0.0, -100.0, m)
    a0 = s.cumulative_adhesion
    update_state(s, 30.0, -100.0, m)
    a1 = s.cumulative_adhesion
    update_state(s, 120.0, -100.0, m)
    a2 = s.cumulative_adhesion
    assert a0 <= a1 <= a2
    assert a2 > 0.3


def test_swallow_clears_adhesion():
    m = default_healthy_mechanics()
    s = MuscleState(cumulative_adhesion=0.8)
    record_swallow(s, 10.0)
    assert s.cumulative_adhesion < 0.2


def test_dysfunctional_mechanics_worse_than_healthy_on_rapid_descent():
    r_h = simulate(PatientState(), RAPID_DESCENT_10K_FT_MIN,
                    muscle_mechanics=default_healthy_mechanics(), rng_seed=7)
    r_d = simulate(PatientState(), RAPID_DESCENT_10K_FT_MIN,
                    muscle_mechanics=default_dysfunctional_mechanics(), rng_seed=7)
    # Dysfunction should be at least as bad (usually worse)
    assert r_d.risk.p_barotitis >= r_h.risk.p_barotitis - 1e-6


def test_muscle_state_increments_time():
    m = default_healthy_mechanics()
    s = MuscleState()
    update_state(s, 10.0, -50.0, m)
    update_state(s, 20.0, -50.0, m)
    assert s.cumulative_adhesion > 0
