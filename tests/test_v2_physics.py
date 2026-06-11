"""
Physics regression tests for v2.

These verify the qualitative behavior of the Kanick-Doyle-extended engine:
healthy subjects keep ΔP in the "barotitis-safe" range on standard chamber
profiles, severe descent rates grow ΔP faster than equalization can clear it,
and the Patulous-S1 override keeps ΔP = 0 exactly.
"""

from __future__ import annotations

import numpy as np
import pytest

from barotrauma.v2 import (
    FAC_BOGOTA_DEFAULT,
    GROTH_1986_VALIDATION,
    RAPID_DESCENT_10K_FT_MIN,
    SLOW_DESCENT_1K_FT_MIN,
    USAFSAM_TYPE_I,
    EtFunction,
    PatientState,
    simulate,
)
from barotrauma.v2 import constants as C


def test_altitude_pressure_monotonic():
    from barotrauma.v2.atmosphere import altitude_to_pressure_mmHg, pressure_to_altitude_ft

    # U.S. Standard Atmosphere pressure-altitude checkpoints.
    assert float(altitude_to_pressure_mmHg(0.0)) == pytest.approx(760.0, abs=0.01)
    assert float(altitude_to_pressure_mmHg(8530.0)) == pytest.approx(553.17, abs=0.05)
    assert float(altitude_to_pressure_mmHg(25000.0)) == pytest.approx(282.03, abs=0.05)
    assert float(altitude_to_pressure_mmHg(35000.0)) == pytest.approx(178.84, abs=0.05)
    # Strict monotonic decrease
    alts = np.array([0, 5000, 10000, 15000, 20000, 25000, 30000, 35000])
    ps = altitude_to_pressure_mmHg(alts.astype(float))
    assert np.all(np.diff(ps) < 0)
    assert pressure_to_altitude_ft(ps) == pytest.approx(alts, abs=0.05)


def test_groth_1986_parity_order_of_magnitude():
    """
    Kanick-Doyle 2005 Fig 3 reports ΔP in mmH2O tens-to-hundreds during the
    25-second Groth pressure-chamber cycle. At 1920 ft/min for 25 s
    (equivalent to ~800 ft) a healthy ear should tolerate this easily.
    """
    result = simulate(PatientState(), GROTH_1986_VALIDATION, dt_s=0.05)
    # Quick profile, healthy: p_barotitis should be tiny, ΔP limited
    assert result.risk.p_barotitis < 0.02, f"p_baro {result.risk.p_barotitis}"
    assert result.risk.max_abs_delta_p_mmHg < 30.0


def test_slow_vs_rapid_descent_monotonicity():
    """
    Peak |ΔP| and the super-linear rupture hazard increase with descent rate.
    Barotitis is NOT monotonic because dose-time-integral also matters — a
    slow-but-long descent may accumulate more barotitis dose than a fast-but-
    short descent despite lower peak |ΔP|.
    """
    patient = PatientState(et=EtFunction(severity="mild"))
    slow = simulate(patient, SLOW_DESCENT_1K_FT_MIN)
    rapid = simulate(patient, RAPID_DESCENT_10K_FT_MIN)
    # Peak pressure must rise with descent rate
    assert rapid.risk.max_abs_delta_p_mmHg > slow.risk.max_abs_delta_p_mmHg
    # Rupture hazard (cubic on excess) is dominated by peak and thus
    # monotonic with descent rate.
    assert rapid.risk.p_rupture >= slow.risk.p_rupture


def test_healthy_baseline_fac_is_low_risk():
    result = simulate(PatientState(), FAC_BOGOTA_DEFAULT)
    # Per Italian AF / FAC anchors: healthy pre-screened aircrew should be
    # well under 5% per-exposure.
    assert result.risk.p_barotitis < 0.05
    assert result.risk.risk_category() in ("low", "moderate")


def test_patulous_s1_zero_delta_p():
    """Kanick-Doyle (2005 p.334) predicts PET = ΔP = 0 throughout flight."""
    result = simulate(
        PatientState(pet="s1"),
        RAPID_DESCENT_10K_FT_MIN,
        dt_s=0.05,
    )
    # Exact zero is enforced by apply_patulous_state hard-zero override
    assert result.risk.max_abs_delta_p_mmHg == pytest.approx(0.0, abs=1e-9)
    assert result.risk.p_barotitis == pytest.approx(0.0)


def test_tm_displacement_clamps_at_max():
    from barotrauma.v2.middle_ear import tm_displacement_ml
    from barotrauma.v2.types import PatientAnatomy

    anat = PatientAnatomy()
    # Huge positive ΔP clamps at +Vtm_max
    assert tm_displacement_ml(10_000.0, anat) == pytest.approx(anat.tm_max_displacement_ml)
    # Huge negative ΔP clamps at -Vtm_max
    assert tm_displacement_ml(-10_000.0, anat) == pytest.approx(-anat.tm_max_displacement_ml)


def test_trace_length_and_shape():
    result = simulate(PatientState(), USAFSAM_TYPE_I, dt_s=0.5)
    t = result.trace.t_s
    # Sanity: time axis, pressures, and ΔP have identical length
    assert len(t) == len(result.trace.p_ambient_mmHg)
    assert len(t) == len(result.trace.delta_p_mmHg)
    # Time is strictly increasing
    assert np.all(np.diff(t) > 0)
