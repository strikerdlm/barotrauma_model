"""
Hybrid physics-ML head tests.
"""

from __future__ import annotations

import numpy as np
import pytest

from barotrauma.v2 import (
    FAC_BOGOTA_DEFAULT,
    PatientState,
    PhysicsMLPredictor,
)
from barotrauma.v2.ml_hybrid import extract_features
from barotrauma.v2.types import EtFunction


def _toy_cohort(n_pos: int = 8, n_neg: int = 22, rng_seed: int = 1):
    """Build a small toy cohort with clearly separable positive/negative classes."""
    rng = np.random.default_rng(rng_seed)
    patients: list[PatientState] = []
    outcomes: list[int] = []
    # positives: high-risk states
    for _ in range(n_pos):
        patients.append(PatientState(
            uri="day_4_7",
            et=EtFunction(severity="severe"),
        ))
        outcomes.append(1)
    # negatives: healthy state
    for _ in range(n_neg):
        patients.append(PatientState(uri="none"))
        outcomes.append(0)
    # Shuffle
    idx = rng.permutation(len(patients))
    return [patients[i] for i in idx], [outcomes[i] for i in idx]


def test_extract_features_shape_stable():
    p1 = PatientState()
    p2 = PatientState(uri="day_4_7", pet="s2", medication="intranasal_steroid")
    f1 = extract_features(p1, FAC_BOGOTA_DEFAULT, dt_s=0.5)
    f2 = extract_features(p2, FAC_BOGOTA_DEFAULT, dt_s=0.5)
    assert f1.shape == f2.shape
    # Clinical one-hots should differ
    assert not np.allclose(f1, f2)


def test_predictor_passthrough_when_unfit():
    predictor = PhysicsMLPredictor(profile=FAC_BOGOTA_DEFAULT, dt_s=0.5)
    p = PatientState()
    pred = predictor.predict_proba(p)
    assert pred.used_ml is False
    assert pred.physics_p == pred.corrected_p
    assert pred.ci_lower is None
    assert pred.ci_upper is None


def test_predictor_fit_requires_both_classes():
    predictor = PhysicsMLPredictor(profile=FAC_BOGOTA_DEFAULT, dt_s=0.5)
    patients = [PatientState(), PatientState()]
    outcomes = [0, 0]                          # all negative
    with pytest.raises(ValueError):
        predictor.fit(patients, outcomes)


def test_predictor_fit_and_predict_roundtrip():
    predictor = PhysicsMLPredictor(
        profile=FAC_BOGOTA_DEFAULT,
        bootstrap_samples=12,
        dt_s=0.5,
    )
    patients, outcomes = _toy_cohort(n_pos=8, n_neg=22)
    predictor.fit(patients, outcomes)

    # Positive example: high-risk patient
    high = PatientState(uri="day_4_7", et=EtFunction(severity="severe"))
    low = PatientState(uri="none")
    pred_high = predictor.predict_proba(high, with_uncertainty=True)
    pred_low = predictor.predict_proba(low, with_uncertainty=True)

    assert pred_high.used_ml
    assert pred_low.used_ml
    # High-risk predicted probability should exceed low-risk
    assert pred_high.corrected_p > pred_low.corrected_p
    # CI fields populated
    assert pred_high.ci_lower is not None and pred_high.ci_upper is not None
    assert pred_high.ci_lower <= pred_high.corrected_p <= pred_high.ci_upper + 0.01


def test_predictor_evaluate_returns_metrics():
    predictor = PhysicsMLPredictor(
        profile=FAC_BOGOTA_DEFAULT,
        bootstrap_samples=6,
        dt_s=0.5,
    )
    patients, outcomes = _toy_cohort(n_pos=8, n_neg=22, rng_seed=7)
    predictor.fit(patients, outcomes)
    test_p, test_y = _toy_cohort(n_pos=4, n_neg=8, rng_seed=99)
    metrics = predictor.evaluate(test_p, test_y)
    assert 0.0 <= metrics.brier <= 1.0
    assert 0.0 <= metrics.calibration_error <= 1.0
    assert not np.isnan(metrics.auroc)
    assert metrics.n_samples == 12
