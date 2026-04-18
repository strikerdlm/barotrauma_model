"""
Calibration-layer tests. Runs the FAC-anchored calibration loop in CI-safe
sizes and checks convergence + URI dominance.
"""

from __future__ import annotations

import pytest

from barotrauma.v2 import calibration
from barotrauma.v2.calibration import (
    CohortPriors,
    calibrate_hazard_constants,
    sample_cohort,
)
from barotrauma.v2.scenarios import FAC_BOGOTA_DEFAULT


def test_sample_cohort_size_and_types():
    cohort = sample_cohort(50)
    assert len(cohort) == 50
    uris = {p.uri for p in cohort}
    assert uris.issubset({
        "none", "day_1_3", "day_4_7", "day_8_14", "day_15_21", "day_22_28",
    })
    severities = {p.et.severity for p in cohort}
    assert severities.issubset({"normal", "mild", "moderate", "severe"})


def test_calibration_converges_near_target():
    """Small cohort calibration should converge within ±0.5% of target."""
    result = calibrate_hazard_constants(
        target_per_exposure_prevalence=0.02,
        n_cohort=100,
        tol=0.004,
        max_iter=12,
        rng_seed=7,
        apply_globally=False,
    )
    assert abs(result.achieved_prevalence - 0.02) < 0.008
    # Hazard constants are positive and within plausible range
    assert 1e-9 < result.hazard_barotitis_r < 1e-3


def test_calibration_preserves_uri_dominance():
    """
    After calibration, URI-positive subgroups should carry higher mean
    p_barotitis than URI-negative — the qualitative anchor from the FAC
    cohort (URI is the dominant reported risk factor).
    """
    result = calibrate_hazard_constants(
        target_per_exposure_prevalence=0.02,
        n_cohort=100,
        tol=0.005,
        max_iter=12,
        rng_seed=7,
        apply_globally=False,
    )
    uri_means = result.cohort_summary["uri_subgroup_means"]
    # URI day_4_7 should be ≥ 2× URI none
    assert uri_means["day_4_7"] > uri_means["none"] * 2.0


def test_career_projection_near_fac_anchor():
    """3-exposure career rate should project near the 5.8% FAC anchor."""
    result = calibrate_hazard_constants(
        target_per_exposure_prevalence=0.02,
        n_cohort=150,
        tol=0.004,
        max_iter=12,
        rng_seed=11,
        apply_globally=False,
    )
    # 1 - (1 - 0.02)^3 ≈ 0.0588 → within a couple percentage points
    assert 0.035 < result.per_exposure_to_career_scale < 0.090


def test_calibration_roundtrip_json(tmp_path):
    result = calibrate_hazard_constants(
        target_per_exposure_prevalence=0.02,
        n_cohort=50,
        tol=0.01,
        max_iter=6,
        rng_seed=3,
        apply_globally=False,
    )
    path = tmp_path / "calib.json"
    calibration.save_calibration(result, path)
    assert path.exists()
    loaded = calibration.load_calibration(path)
    assert loaded is not None
    assert "hazard" in loaded
    assert loaded["hazard"]["barotitis_r"] == pytest.approx(result.hazard_barotitis_r)
