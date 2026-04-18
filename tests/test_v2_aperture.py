"""
Tests for the ascent/descent asymmetric aperture model (v2.1).
"""

from __future__ import annotations

import numpy as np
import pytest

from barotrauma.v2 import PatientState, simulate
from barotrauma.v2.et_dynamics import aperture_factor
from barotrauma.v2.pathophysiology import Modifiers
from barotrauma.v2.types import ChamberProfile, ChamberSegment, EtFunction


def _descent_profile(rate_ft_min: float) -> ChamberProfile:
    duration = 25000.0 / rate_ft_min * 60.0
    return ChamberProfile(
        name=f"descent {rate_ft_min:.0f} ft/min",
        start_altitude_ft=25000.0,
        segments=(ChamberSegment(duration_s=duration, end_altitude_ft=0,
                                 label="descent"),),
    )


# ---------------------------- aperture_factor unit tests ----------------------
def test_aperture_full_on_ascent():
    et = EtFunction()
    m = Modifiers()
    # Positive ΔP → cheap venting, aperture 1.0
    assert aperture_factor(50.0, rate_mmHg_s=0.0, et=et, modifiers=m) == pytest.approx(1.0)
    assert aperture_factor(200.0, rate_mmHg_s=0.0, et=et, modifiers=m) == pytest.approx(1.0)


def test_aperture_free_zone_on_descent():
    """Below the free-zone cutoff (~40 mmHg) healthy descent keeps full aperture."""
    et = EtFunction()
    m = Modifiers()
    assert aperture_factor(-30.0, 0.0, et, m) == pytest.approx(1.0)
    assert aperture_factor(-10.0, 0.0, et, m) == pytest.approx(1.0)


def test_aperture_collapses_with_descent_delta_p():
    et = EtFunction()
    m = Modifiers()
    a_60 = aperture_factor(-60.0, 0.0, et, m)
    a_120 = aperture_factor(-120.0, 0.0, et, m)
    a_200 = aperture_factor(-200.0, 0.0, et, m)
    # Monotonic decrease
    assert 1.0 > a_60 > a_120 > a_200 > 0.0


def test_aperture_rate_tightening():
    """Faster pressure change tightens the descent aperture."""
    et = EtFunction()
    m = Modifiers()
    slow = aperture_factor(-120.0, rate_mmHg_s=0.1, et=et, modifiers=m)
    fast = aperture_factor(-120.0, rate_mmHg_s=3.0, et=et, modifiers=m)
    assert fast < slow


def test_aperture_inflammation_tightening():
    """URI / inflammation (higher ra_mult) collapses the lumen at lower ΔP."""
    et = EtFunction()
    healthy = aperture_factor(-120.0, 0.0, et, Modifiers())
    uri = aperture_factor(-120.0, 0.0, et, Modifiers(ra_mult=4.0))
    assert uri < healthy


# ----------------------- end-to-end asymmetry behaviour -----------------------
def test_healthy_slow_descent_is_low_risk():
    """300 ft/min matches commercial cabin physiology — healthy pilots fine."""
    r = simulate(PatientState(), _descent_profile(300))
    assert r.risk.p_barotitis < 0.01
    assert r.risk.max_abs_delta_p_mmHg < 50.0


def test_medium_descent_is_highest_barotitis_risk():
    """
    Clinically, 2000-3000 ft/min is the worst zone for barotitis — slow
    enough for sustained exposure, fast enough for aperture to collapse.
    Faster descents shorten exposure time and lower cumulative risk (though
    p_rupture keeps rising). This matches Italian AF chamber observations.
    """
    rates = [500, 1000, 2000, 3000, 5000, 7500, 10000]
    p_baros = []
    for rate in rates:
        r = simulate(PatientState(), _descent_profile(rate))
        p_baros.append(r.risk.p_barotitis)

    peak_idx = int(np.argmax(p_baros))
    peak_rate = rates[peak_idx]
    assert 1000 <= peak_rate <= 5000, (
        f"expected peak at 1000-5000 ft/min, got {peak_rate}: {p_baros}"
    )


def test_peak_pressure_saturates_with_descent_rate():
    """
    Max |ΔP| must grow monotonically until lumen collapse plateaus. p_rupture
    ordering is: ~0 at slow descent, nonzero at rapid (2000+ ft/min).
    Strict monotonicity of p_rupture is NOT enforced because at very high
    rates the short exposure time partially offsets the cubic-on-peak hazard.
    """
    rates = [500, 1000, 2000, 5000, 10000]
    peaks = []
    ruptures = []
    for rate in rates:
        r = simulate(PatientState(), _descent_profile(rate))
        peaks.append(r.risk.max_abs_delta_p_mmHg)
        ruptures.append(r.risk.p_rupture)
    # Peak pressure monotonic in rate (with minor saturation wiggle allowed)
    for i in range(1, len(peaks)):
        assert peaks[i] >= peaks[i - 1] - 5.0
    # Rupture risk: near-zero for slow, nonzero for ≥2000 ft/min
    assert ruptures[0] < 1e-3             # 500 ft/min
    assert ruptures[1] < 1e-3             # 1000 ft/min
    assert max(ruptures[2:]) > 1e-3       # some fast-rate runs do trigger


def test_ascent_alone_is_low_risk():
    """Ascent-only profile should produce near-zero MEB risk (Boyle buffering +
    passive ME-side venting)."""
    prof = ChamberProfile(
        name="ascent only",
        start_altitude_ft=0.0,
        segments=(ChamberSegment(duration_s=900, end_altitude_ft=25000,
                                 label="ascent 1670 ft/min"),),
    )
    r = simulate(PatientState(), prof)
    assert r.risk.p_barotitis < 0.02
    assert r.risk.p_rupture < 1e-4
