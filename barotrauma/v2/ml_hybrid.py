"""
barotrauma.v2.ml_hybrid
=======================

Hybrid physics-ML predictor. Wraps the deterministic v2 simulator with an
optional residual-correction layer that can be trained on labeled
outcome data, returning calibrated probabilities with uncertainty
intervals. Falls through to the physics-only prediction when unfit, so
the same interface works whether or not training data is available.

Design (research brief 05 §2, §5)
---------------------------------
1. Physics extracts a feature vector per patient-exposure:
   (p_barotitis, p_baromyringitis, p_rupture, max|ΔP|, AUC above barotitis
   threshold, AUC above baromyringitis threshold, time above rupture
   threshold).
2. Clinical one-hot features are concatenated (URI state, PET state,
   severity class, rhinitis, medication).
3. A GradientBoostingClassifier is trained on (features, binary outcome).
4. Predictions are Platt- / isotonic-scaled for calibration.
5. Uncertainty via bootstrap on the training set (80 resamples → 5/95th
   percentile of the calibrated probability distribution).

Without training data the predictor is a thin pass-through to
``simulate().risk.p_barotitis``. This is the correct safe default — we
deliberately **do not** emit phantom ML predictions the research-brief-05
'don't ship untrained scaffolding' guardrail warns against.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Sequence

import numpy as np
from numpy.typing import NDArray

from . import constants as C
from .engine import simulate
from .scenarios import FAC_BOGOTA_DEFAULT
from .types import (
    ChamberProfile,
    ChronicRhinitis,
    EtSeverity,
    MedicationEffect,
    PatientState,
    PetState,
    UriState,
)

try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import brier_score_loss, roc_auc_score
    _SKLEARN_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SKLEARN_AVAILABLE = False


_URI_LEVELS: tuple[UriState, ...] = (
    "none", "day_1_3", "day_4_7", "day_8_14", "day_15_21", "day_22_28",
)
_PET_LEVELS: tuple[PetState, ...] = ("normal", "s1", "s2", "s3", "s4")
_SEV_LEVELS: tuple[EtSeverity, ...] = ("normal", "mild", "moderate", "severe")
_RHIN_LEVELS: tuple[ChronicRhinitis, ...] = (
    "none", "allergic", "chronic_rhinosinusitis",
)
_MED_LEVELS: tuple[MedicationEffect, ...] = (
    "none", "pseudoephedrine_oral", "oxymetazoline_topical",
    "intranasal_steroid", "antihistamine_spray",
)


# ------------------------------------------------ feature extraction --
def extract_features(
    patient: PatientState,
    profile: ChamberProfile,
    *,
    dt_s: float = 0.5,
) -> NDArray[np.float64]:
    """
    Extract a feature vector combining physics outputs + clinical one-hot
    encodings for a single patient-exposure.

    Returns an array of shape (n_features,). Order is stable across calls
    to make Gradient Boosting inspection easy.
    """
    result = simulate(patient, profile, dt_s=dt_s)
    trace = result.trace
    risk = result.risk

    physics = np.array([
        risk.p_barotitis,
        risk.p_baromyringitis,
        risk.p_rupture,
        risk.max_abs_delta_p_mmHg,
        trace.auc_abs_delta_p(C.BAROTITIS_THRESHOLD_MMHG),
        trace.auc_abs_delta_p(C.BAROMYRINGITIS_THRESHOLD_MMHG),
        trace.time_above(C.RUPTURE_THRESHOLD_MMHG),
        float(patient.anatomy.mastoid_volume_ml),
        float(patient.anatomy.age_years),
        float(patient.previous_meb),
        float(patient.habitual_sniffer),
    ], dtype=np.float64)

    clinical = np.concatenate([
        _one_hot(patient.uri, _URI_LEVELS),
        _one_hot(patient.pet, _PET_LEVELS),
        _one_hot(patient.et.severity, _SEV_LEVELS),
        _one_hot(patient.rhinitis, _RHIN_LEVELS),
        _one_hot(patient.medication, _MED_LEVELS),
    ])

    return np.concatenate([physics, clinical])


def _one_hot(value: str, levels: tuple[str, ...]) -> NDArray[np.float64]:
    out = np.zeros(len(levels), dtype=np.float64)
    if value in levels:
        out[levels.index(value)] = 1.0
    return out


# -------------------------------------------------- predictor class ---
@dataclass
class HybridPrediction:
    """One prediction output with uncertainty."""

    physics_p: float
    corrected_p: float
    ci_lower: float | None
    ci_upper: float | None
    used_ml: bool
    features_shape: int


@dataclass
class HybridEvaluation:
    """Held-out evaluation metrics."""

    brier: float
    auroc: float
    n_samples: int
    calibration_error: float | None = None


class PhysicsMLPredictor:
    """
    Hybrid physics-ML predictor for per-exposure MEB risk.

    Workflow
    --------
    >>> predictor = PhysicsMLPredictor(profile=FAC_BOGOTA_DEFAULT)
    >>> # Without training data:
    >>> predictor.predict_proba(patient)       # physics pass-through
    >>> # With training data:
    >>> predictor.fit(patients, outcomes)
    >>> predictor.predict_proba(patient, with_uncertainty=True)

    The class is deliberately narrow — no cross-validation, no
    hyperparameter search, no deep learning. Research brief 05 emphasizes
    that with a small labeled cohort (N ~ 100s) the safe default is a
    tree ensemble with isotonic calibration. Add complexity only if a
    real cohort justifies it.
    """

    def __init__(
        self,
        profile: ChamberProfile = FAC_BOGOTA_DEFAULT,
        *,
        n_estimators: int = 200,
        max_depth: int = 3,
        learning_rate: float = 0.05,
        bootstrap_samples: int = 80,
        dt_s: float = 0.5,
        random_state: int = 42,
    ):
        self.profile = profile
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.bootstrap_samples = bootstrap_samples
        self.dt_s = dt_s
        self.random_state = random_state

        self._model: Any = None
        self._bootstrap_models: list[Any] = []
        self._fitted: bool = False
        self._feature_size: int = 0

    # -------------------------------------------------- feature matrix -
    def _build_feature_matrix(
        self, patients: Sequence[PatientState]
    ) -> NDArray[np.float64]:
        return np.vstack([
            extract_features(p, self.profile, dt_s=self.dt_s)
            for p in patients
        ])

    # ------------------------------------------------------- fit ------
    def fit(
        self,
        patients: Sequence[PatientState],
        outcomes: Sequence[int],
    ) -> "PhysicsMLPredictor":
        """Train the residual-correction model on labeled data."""
        if not _SKLEARN_AVAILABLE:
            raise RuntimeError(
                "sklearn is required for PhysicsMLPredictor.fit(); install scikit-learn"
            )
        if len(patients) != len(outcomes):
            raise ValueError("patients and outcomes must be same length")
        if len(set(outcomes)) < 2:
            raise ValueError(
                "fit requires at least one positive and one negative outcome"
            )

        X = self._build_feature_matrix(patients)
        y = np.asarray(outcomes, dtype=np.int64)
        self._feature_size = X.shape[1]

        base = GradientBoostingClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=self.random_state,
        )
        # Isotonic calibration requires ≥1 positive per fold — use prefit when
        # the cohort is small.
        cv = 3 if len(y) >= 30 and np.sum(y) >= 3 else "prefit"
        if cv == "prefit":
            base.fit(X, y)
            self._model = CalibratedClassifierCV(base, method="isotonic", cv="prefit")
            self._model.fit(X, y)
        else:
            self._model = CalibratedClassifierCV(base, method="isotonic", cv=cv)
            self._model.fit(X, y)

        # Bootstrap models for CI
        rng = np.random.default_rng(self.random_state)
        self._bootstrap_models = []
        for b in range(self.bootstrap_samples):
            idx = rng.integers(0, len(y), size=len(y))
            if len(set(y[idx])) < 2:
                continue
            boot = GradientBoostingClassifier(
                n_estimators=max(50, self.n_estimators // 2),
                max_depth=self.max_depth,
                learning_rate=self.learning_rate,
                random_state=self.random_state + b + 1,
            )
            boot.fit(X[idx], y[idx])
            self._bootstrap_models.append(boot)

        self._fitted = True
        return self

    # ----------------------------------------------------- predict ---
    def predict_proba(
        self,
        patient: PatientState,
        *,
        with_uncertainty: bool = False,
    ) -> HybridPrediction:
        """
        Return a calibrated probability of per-exposure MEB.

        When unfit, falls through to the physics p_barotitis (CI fields
        are None). When fit, returns the calibrated model output plus
        bootstrap 90% CI when ``with_uncertainty`` is True.
        """
        physics_result = simulate(patient, self.profile, dt_s=self.dt_s)
        physics_p = float(physics_result.risk.p_barotitis)

        if not self._fitted or self._model is None:
            return HybridPrediction(
                physics_p=physics_p,
                corrected_p=physics_p,
                ci_lower=None,
                ci_upper=None,
                used_ml=False,
                features_shape=0,
            )

        x = extract_features(patient, self.profile, dt_s=self.dt_s)[None, :]
        prob = float(self._model.predict_proba(x)[0, 1])

        ci_lo: float | None = None
        ci_hi: float | None = None
        if with_uncertainty and self._bootstrap_models:
            probs = np.asarray(
                [m.predict_proba(x)[0, 1] for m in self._bootstrap_models]
            )
            ci_lo = float(np.quantile(probs, 0.05))
            ci_hi = float(np.quantile(probs, 0.95))

        return HybridPrediction(
            physics_p=physics_p,
            corrected_p=prob,
            ci_lower=ci_lo,
            ci_upper=ci_hi,
            used_ml=True,
            features_shape=x.shape[1],
        )

    # ------------------------------------------------------ evaluate ---
    def evaluate(
        self,
        patients: Sequence[PatientState],
        outcomes: Sequence[int],
    ) -> HybridEvaluation:
        """Compute Brier, AUROC, expected calibration error on held-out data."""
        if not self._fitted:
            raise RuntimeError("predictor is not fit")
        X = self._build_feature_matrix(patients)
        y = np.asarray(outcomes, dtype=np.int64)
        probs = self._model.predict_proba(X)[:, 1]
        brier = float(brier_score_loss(y, probs))
        try:
            auroc = float(roc_auc_score(y, probs))
        except ValueError:
            auroc = float("nan")
        ece = float(_expected_calibration_error(y, probs, n_bins=10))
        return HybridEvaluation(
            brier=brier,
            auroc=auroc,
            n_samples=len(y),
            calibration_error=ece,
        )


def _expected_calibration_error(
    y: NDArray[np.int64],
    probs: NDArray[np.float64],
    n_bins: int = 10,
) -> float:
    """Equal-width-bin ECE."""
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y)
    for i in range(n_bins):
        lo, hi = bin_edges[i], bin_edges[i + 1]
        mask = (probs >= lo) & (probs < hi if i < n_bins - 1 else probs <= hi)
        if not np.any(mask):
            continue
        bin_p = float(np.mean(probs[mask]))
        bin_y = float(np.mean(y[mask]))
        ece += (np.sum(mask) / n) * abs(bin_p - bin_y)
    return float(ece)
