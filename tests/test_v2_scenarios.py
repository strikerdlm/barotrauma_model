"""
Preset chamber profile sanity checks.
"""

from __future__ import annotations

import numpy as np
import pytest

from barotrauma.v2 import PRESETS, PatientState, get_profile, simulate


@pytest.mark.parametrize("name", list(PRESETS.keys()))
def test_all_presets_validate(name):
    profile = get_profile(name)
    profile.validate()
    assert profile.total_duration_s() > 0


@pytest.mark.parametrize("name", ["usafsam_type_i", "fac_bogota_default",
                                   "commercial_cabin_descent", "groth_1986"])
def test_all_presets_simulate_without_error(name):
    profile = get_profile(name)
    result = simulate(PatientState(), profile)
    assert np.isfinite(result.risk.p_barotitis)
    assert 0.0 <= result.risk.p_barotitis <= 1.0


def test_fac_profile_starts_at_bogota():
    profile = get_profile("fac_bogota_default")
    assert profile.start_altitude_ft > 8000  # Bogotá elevation


def test_usafsam_type_ii_has_rapid_decompression_segment():
    profile = get_profile("usafsam_type_ii_rd")
    rd_segments = [s for s in profile.segments if "RD" in s.label]
    assert len(rd_segments) == 1
    assert rd_segments[0].duration_s <= 2.0


def test_unknown_profile_raises():
    with pytest.raises(KeyError):
        get_profile("no_such_profile")
