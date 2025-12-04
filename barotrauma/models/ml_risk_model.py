"""
Machine Learning Model for Barotrauma Risk Prediction.

This module implements trainable ML models for predicting middle ear barotrauma
risk based on Valsalva maneuver video analysis features.

Model Types
-----------
1. LogisticRegressionModel: Interpretable baseline model
2. GradientBoostingModel: Higher accuracy ensemble model
3. HybridPhysicsMLModel: Combines physics-based simulation with ML correction

Training Data
-------------
The models are designed to be trained on:
- Valsalva video analysis features from both ears
- Clinical history variables
- Known outcomes from hypobaric chamber exposures (controls)

Clinical Validation
-------------------
Models include calibration assessment and should be validated against:
- AUC-ROC for discrimination
- Brier score for calibration
- Net benefit for clinical utility

Author: Aerospace Medicine Research
License: MIT
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

# Type alias
FloatArray = NDArray[np.floating[Any]]

# Conditional imports
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import (
        roc_auc_score,
        brier_score_loss,
        classification_report,
    )
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class TrainingExample:
    """Single training example for ML model."""
    # Features from Valsalva analysis
    left_max_displacement: float
    left_response_latency: float
    left_movement_smoothness: float
    left_movement_completeness: float
    right_max_displacement: float
    right_response_latency: float
    right_movement_smoothness: float
    right_movement_completeness: float
    asymmetry_score: float
    
    # Clinical features
    age: int
    previous_barotrauma: bool
    chronic_et_dysfunction: bool
    current_uri: bool
    
    # Outcome (target variable)
    outcome: str  # "no_barotrauma", "mild", "moderate", "severe"
    
    # Metadata
    patient_id: str = ""
    is_control: bool = False
    
    def to_feature_vector(self) -> FloatArray:
        """Convert to numpy feature vector."""
        return np.array([
            self.left_max_displacement,
            self.left_response_latency,
            self.left_movement_smoothness,
            self.left_movement_completeness,
            self.right_max_displacement,
            self.right_response_latency,
            self.right_movement_smoothness,
            self.right_movement_completeness,
            self.asymmetry_score,
            float(self.age) / 100.0,  # Normalize age
            float(self.previous_barotrauma),
            float(self.chronic_et_dysfunction),
            float(self.current_uri),
        ], dtype=np.float64)
    
    def to_binary_outcome(self) -> int:
        """Convert outcome to binary (0 = no/mild, 1 = moderate/severe)."""
        if self.outcome in ("no_barotrauma", "mild"):
            return 0
        return 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'left_max_displacement': self.left_max_displacement,
            'left_response_latency': self.left_response_latency,
            'left_movement_smoothness': self.left_movement_smoothness,
            'left_movement_completeness': self.left_movement_completeness,
            'right_max_displacement': self.right_max_displacement,
            'right_response_latency': self.right_response_latency,
            'right_movement_smoothness': self.right_movement_smoothness,
            'right_movement_completeness': self.right_movement_completeness,
            'asymmetry_score': self.asymmetry_score,
            'age': self.age,
            'previous_barotrauma': self.previous_barotrauma,
            'chronic_et_dysfunction': self.chronic_et_dysfunction,
            'current_uri': self.current_uri,
            'outcome': self.outcome,
            'patient_id': self.patient_id,
            'is_control': self.is_control,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrainingExample':
        """Create from dictionary."""
        return cls(
            left_max_displacement=data['left_max_displacement'],
            left_response_latency=data['left_response_latency'],
            left_movement_smoothness=data['left_movement_smoothness'],
            left_movement_completeness=data['left_movement_completeness'],
            right_max_displacement=data['right_max_displacement'],
            right_response_latency=data['right_response_latency'],
            right_movement_smoothness=data['right_movement_smoothness'],
            right_movement_completeness=data['right_movement_completeness'],
            asymmetry_score=data['asymmetry_score'],
            age=data['age'],
            previous_barotrauma=data['previous_barotrauma'],
            chronic_et_dysfunction=data['chronic_et_dysfunction'],
            current_uri=data['current_uri'],
            outcome=data['outcome'],
            patient_id=data.get('patient_id', ''),
            is_control=data.get('is_control', False),
        )


FEATURE_NAMES = [
    'left_max_displacement',
    'left_response_latency',
    'left_movement_smoothness',
    'left_movement_completeness',
    'right_max_displacement',
    'right_response_latency',
    'right_movement_smoothness',
    'right_movement_completeness',
    'asymmetry_score',
    'normalized_age',
    'previous_barotrauma',
    'chronic_et_dysfunction',
    'current_uri',
]


# ============================================================================
# Model Metrics
# ============================================================================

@dataclass
class ModelMetrics:
    """Performance metrics for ML model."""
    auc_roc: float
    brier_score: float
    accuracy: float
    sensitivity: float
    specificity: float
    ppv: float  # Positive predictive value
    npv: float  # Negative predictive value
    cv_scores: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'auc_roc': self.auc_roc,
            'brier_score': self.brier_score,
            'accuracy': self.accuracy,
            'sensitivity': self.sensitivity,
            'specificity': self.specificity,
            'ppv': self.ppv,
            'npv': self.npv,
            'cv_scores': self.cv_scores,
        }


# ============================================================================
# Base Model Class
# ============================================================================

class BarotraumaRiskModel(ABC):
    """Abstract base class for barotrauma risk prediction models."""
    
    def __init__(self) -> None:
        """Initialize model."""
        self.logger = logging.getLogger(__name__)
        self.is_trained = False
        self._scaler: Optional[Any] = None  # StandardScaler
        self._training_examples: List[TrainingExample] = []
    
    @abstractmethod
    def train(self, examples: List[TrainingExample]) -> ModelMetrics:
        """
        Train model on labeled examples.
        
        Args:
            examples: List of training examples with known outcomes
            
        Returns:
            ModelMetrics with training performance
        """
        pass
    
    @abstractmethod
    def predict_proba(self, example: TrainingExample) -> float:
        """
        Predict probability of significant barotrauma.
        
        Args:
            example: Features for prediction (outcome can be empty)
            
        Returns:
            Probability of moderate/severe barotrauma (0-1)
        """
        pass
    
    def predict(self, example: TrainingExample, threshold: float = 0.5) -> str:
        """
        Predict barotrauma risk category.
        
        Args:
            example: Features for prediction
            threshold: Probability threshold for high risk
            
        Returns:
            Risk category string
        """
        prob = self.predict_proba(example)
        
        if prob < 0.2:
            return "Low"
        if prob < 0.4:
            return "Low-Moderate"
        if prob < threshold:
            return "Moderate"
        if prob < 0.8:
            return "High"
        return "Very High"
    
    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        pass
    
    def add_training_example(self, example: TrainingExample) -> None:
        """Add single example to training set."""
        self._training_examples.append(example)
        self.logger.info(
            f"Added training example (total: {len(self._training_examples)})"
        )
    
    @abstractmethod
    def save(self, path: Path) -> None:
        """Save model to file."""
        pass
    
    @abstractmethod
    def load(self, path: Path) -> None:
        """Load model from file."""
        pass


# ============================================================================
# Logistic Regression Model
# ============================================================================

class LogisticRegressionModel(BarotraumaRiskModel):
    """
    Logistic regression model for interpretable risk prediction.
    
    Advantages:
    - Interpretable coefficients
    - Provides calibrated probabilities
    - Robust to small sample sizes
    - Clinical explainability
    """
    
    def __init__(self, regularization: float = 1.0) -> None:
        """
        Initialize model.
        
        Args:
            regularization: L2 regularization strength (C parameter inverse)
        """
        super().__init__()
        
        if not SKLEARN_AVAILABLE:
            raise ImportError(
                "scikit-learn required for ML models. "
                "Install with: pip install scikit-learn"
            )
        
        self.regularization = regularization
        self._model: Optional[LogisticRegression] = None
        self._scaler = StandardScaler()
        self._is_fitted = False
    
    def train(self, examples: List[TrainingExample]) -> ModelMetrics:
        """Train logistic regression model."""
        if len(examples) < 10:
            raise ValueError("Need at least 10 examples for training")
        
        # Prepare data
        X = np.array([ex.to_feature_vector() for ex in examples])
        y = np.array([ex.to_binary_outcome() for ex in examples])
        
        # Check class balance
        pos_ratio = np.mean(y)
        if pos_ratio < 0.1 or pos_ratio > 0.9:
            self.logger.warning(
                f"Imbalanced classes: {pos_ratio:.1%} positive. "
                "Consider collecting more data."
            )
        
        # Scale features
        X_scaled = self._scaler.fit_transform(X)
        
        # Train model
        self._model = LogisticRegression(
            C=1.0 / self.regularization,
            class_weight='balanced',
            max_iter=1000,
            random_state=42,
        )
        self._model.fit(X_scaled, y)
        
        # Compute metrics
        y_pred_proba = self._model.predict_proba(X_scaled)[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self._model, X_scaled, y, cv=min(5, len(examples) // 2), scoring='roc_auc'
        ).tolist()
        
        # Compute detailed metrics
        auc = float(roc_auc_score(y, y_pred_proba))
        brier = float(brier_score_loss(y, y_pred_proba))
        
        tp = np.sum((y == 1) & (y_pred == 1))
        tn = np.sum((y == 0) & (y_pred == 0))
        fp = np.sum((y == 0) & (y_pred == 1))
        fn = np.sum((y == 1) & (y_pred == 0))
        
        metrics = ModelMetrics(
            auc_roc=auc,
            brier_score=brier,
            accuracy=float((tp + tn) / len(y)),
            sensitivity=float(tp / (tp + fn + 1e-6)),
            specificity=float(tn / (tn + fp + 1e-6)),
            ppv=float(tp / (tp + fp + 1e-6)),
            npv=float(tn / (tn + fn + 1e-6)),
            cv_scores=cv_scores,
        )
        
        self.is_trained = True
        self._training_examples = examples.copy()
        
        self.logger.info(
            f"Model trained: AUC={auc:.3f}, Brier={brier:.3f}, "
            f"CV AUC={np.mean(cv_scores):.3f}±{np.std(cv_scores):.3f}"
        )
        
        return metrics
    
    def predict_proba(self, example: TrainingExample) -> float:
        """Predict probability of significant barotrauma."""
        if not self.is_trained or self._model is None:
            raise RuntimeError("Model not trained")
        
        X = example.to_feature_vector().reshape(1, -1)
        X_scaled = self._scaler.transform(X)
        
        prob = float(self._model.predict_proba(X_scaled)[0, 1])
        return prob
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from coefficients."""
        if not self.is_trained or self._model is None:
            raise RuntimeError("Model not trained")
        
        coefficients = self._model.coef_[0]
        importance = dict(zip(FEATURE_NAMES, coefficients.tolist()))
        return importance
    
    def get_interpretable_summary(self, example: TrainingExample) -> str:
        """
        Generate interpretable summary of prediction.
        
        Shows contribution of each feature to the prediction.
        """
        if not self.is_trained or self._model is None:
            raise RuntimeError("Model not trained")
        
        X = example.to_feature_vector().reshape(1, -1)
        X_scaled = self._scaler.transform(X)
        
        prob = self.predict_proba(example)
        coefficients = self._model.coef_[0]
        intercept = self._model.intercept_[0]
        
        lines = [
            "Prediction Explanation",
            "=" * 40,
            f"Predicted Probability: {prob:.1%}",
            f"Risk Category: {self.predict(example)}",
            "",
            "Feature Contributions (log-odds):",
            "-" * 40,
        ]
        
        contributions = X_scaled[0] * coefficients
        sorted_indices = np.argsort(np.abs(contributions))[::-1]
        
        for idx in sorted_indices:
            name = FEATURE_NAMES[idx]
            contrib = contributions[idx]
            direction = "↑" if contrib > 0 else "↓"
            lines.append(f"  {name}: {contrib:+.3f} {direction}")
        
        lines.append(f"\nIntercept: {intercept:.3f}")
        
        return "\n".join(lines)
    
    def save(self, path: Path) -> None:
        """Save model to JSON file."""
        if not self.is_trained or self._model is None:
            raise RuntimeError("Model not trained")
        
        data = {
            'model_type': 'logistic_regression',
            'regularization': self.regularization,
            'coefficients': self._model.coef_.tolist(),
            'intercept': self._model.intercept_.tolist(),
            'scaler_mean': self._scaler.mean_.tolist(),
            'scaler_scale': self._scaler.scale_.tolist(),
            'training_examples': [ex.to_dict() for ex in self._training_examples],
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Model saved to {path}")
    
    def load(self, path: Path) -> None:
        """Load model from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        if data['model_type'] != 'logistic_regression':
            raise ValueError("Invalid model type")
        
        self.regularization = data['regularization']
        
        # Reconstruct model
        self._model = LogisticRegression(
            C=1.0 / self.regularization,
            class_weight='balanced',
        )
        self._model.coef_ = np.array(data['coefficients'])
        self._model.intercept_ = np.array(data['intercept'])
        self._model.classes_ = np.array([0, 1])
        
        # Reconstruct scaler
        self._scaler = StandardScaler()
        self._scaler.mean_ = np.array(data['scaler_mean'])
        self._scaler.scale_ = np.array(data['scaler_scale'])
        
        # Load training examples
        self._training_examples = [
            TrainingExample.from_dict(ex) for ex in data['training_examples']
        ]
        
        self.is_trained = True
        self.logger.info(f"Model loaded from {path}")


# ============================================================================
# Gradient Boosting Model
# ============================================================================

class GradientBoostingModel(BarotraumaRiskModel):
    """
    Gradient boosting model for higher accuracy predictions.
    
    Advantages:
    - Better handling of non-linear relationships
    - Automatic feature interactions
    - Higher predictive accuracy
    - Built-in feature importance
    """
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 3,
        learning_rate: float = 0.1,
    ) -> None:
        """
        Initialize model.
        
        Args:
            n_estimators: Number of boosting stages
            max_depth: Maximum depth of individual trees
            learning_rate: Learning rate (shrinkage)
        """
        super().__init__()
        
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for ML models")
        
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        
        self._model: Optional[GradientBoostingClassifier] = None
        self._calibrated_model: Optional[CalibratedClassifierCV] = None
        self._scaler = StandardScaler()
    
    def train(self, examples: List[TrainingExample]) -> ModelMetrics:
        """Train gradient boosting model."""
        if len(examples) < 20:
            raise ValueError("Need at least 20 examples for gradient boosting")
        
        X = np.array([ex.to_feature_vector() for ex in examples])
        y = np.array([ex.to_binary_outcome() for ex in examples])
        
        X_scaled = self._scaler.fit_transform(X)
        
        # Train base model
        self._model = GradientBoostingClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=42,
        )
        
        # Calibrate probabilities
        if len(examples) >= 50:
            self._calibrated_model = CalibratedClassifierCV(
                self._model, cv=5, method='isotonic'
            )
            self._calibrated_model.fit(X_scaled, y)
        else:
            self._model.fit(X_scaled, y)
        
        # Predictions
        if self._calibrated_model is not None:
            y_pred_proba = self._calibrated_model.predict_proba(X_scaled)[:, 1]
        else:
            y_pred_proba = self._model.predict_proba(X_scaled)[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Cross-validation
        cv_folds = min(5, len(examples) // 4)
        cv_scores = cross_val_score(
            self._model, X_scaled, y, cv=cv_folds, scoring='roc_auc'
        ).tolist()
        
        # Metrics
        auc = float(roc_auc_score(y, y_pred_proba))
        brier = float(brier_score_loss(y, y_pred_proba))
        
        tp = np.sum((y == 1) & (y_pred == 1))
        tn = np.sum((y == 0) & (y_pred == 0))
        fp = np.sum((y == 0) & (y_pred == 1))
        fn = np.sum((y == 1) & (y_pred == 0))
        
        metrics = ModelMetrics(
            auc_roc=auc,
            brier_score=brier,
            accuracy=float((tp + tn) / len(y)),
            sensitivity=float(tp / (tp + fn + 1e-6)),
            specificity=float(tn / (tn + fp + 1e-6)),
            ppv=float(tp / (tp + fp + 1e-6)),
            npv=float(tn / (tn + fn + 1e-6)),
            cv_scores=cv_scores,
        )
        
        self.is_trained = True
        self._training_examples = examples.copy()
        
        return metrics
    
    def predict_proba(self, example: TrainingExample) -> float:
        """Predict probability of significant barotrauma."""
        if not self.is_trained:
            raise RuntimeError("Model not trained")
        
        X = example.to_feature_vector().reshape(1, -1)
        X_scaled = self._scaler.transform(X)
        
        if self._calibrated_model is not None:
            prob = float(self._calibrated_model.predict_proba(X_scaled)[0, 1])
        elif self._model is not None:
            prob = float(self._model.predict_proba(X_scaled)[0, 1])
        else:
            raise RuntimeError("Model not trained")
        
        return prob
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from tree ensemble."""
        if not self.is_trained or self._model is None:
            raise RuntimeError("Model not trained")
        
        importance = dict(zip(
            FEATURE_NAMES,
            self._model.feature_importances_.tolist()
        ))
        return importance
    
    def save(self, path: Path) -> None:
        """Save model (requires joblib)."""
        try:
            import joblib
        except ImportError:
            raise ImportError("joblib required for saving GradientBoostingModel")
        
        data = {
            'model': self._model,
            'calibrated_model': self._calibrated_model,
            'scaler': self._scaler,
            'params': {
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth,
                'learning_rate': self.learning_rate,
            },
            'training_examples': [ex.to_dict() for ex in self._training_examples],
        }
        
        joblib.dump(data, path)
        self.logger.info(f"Model saved to {path}")
    
    def load(self, path: Path) -> None:
        """Load model from file."""
        try:
            import joblib
        except ImportError:
            raise ImportError("joblib required for loading GradientBoostingModel")
        
        data = joblib.load(path)
        
        self._model = data['model']
        self._calibrated_model = data['calibrated_model']
        self._scaler = data['scaler']
        
        params = data['params']
        self.n_estimators = params['n_estimators']
        self.max_depth = params['max_depth']
        self.learning_rate = params['learning_rate']
        
        self._training_examples = [
            TrainingExample.from_dict(ex) for ex in data['training_examples']
        ]
        
        self.is_trained = True


# ============================================================================
# Hybrid Physics + ML Model
# ============================================================================

class HybridPhysicsMLModel(BarotraumaRiskModel):
    """
    Hybrid model combining physics-based simulation with ML correction.
    
    This model:
    1. Uses the physics-based chamber risk model for initial prediction
    2. Applies ML-learned corrections based on Valsalva video features
    3. Combines both for improved predictions
    
    Advantages:
    - Leverages domain knowledge from physics model
    - ML corrects for factors not captured in physics
    - More robust with limited training data
    - Maintains physical interpretability
    """
    
    def __init__(
        self,
        physics_weight: float = 0.6,
        ml_weight: float = 0.4,
    ) -> None:
        """
        Initialize hybrid model.
        
        Args:
            physics_weight: Weight for physics-based prediction
            ml_weight: Weight for ML prediction
        """
        super().__init__()
        
        if abs(physics_weight + ml_weight - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")
        
        self.physics_weight = physics_weight
        self.ml_weight = ml_weight
        
        # ML correction model (learns residuals)
        self._ml_model = LogisticRegressionModel(regularization=0.5)
        
        # Import chamber risk model
        self._chamber_model: Optional[Any] = None
        try:
            from .chamber_risk import HypobaricChamberRiskModel
            self._chamber_model = HypobaricChamberRiskModel()
        except ImportError:
            self.logger.warning("Chamber risk model not available")
    
    def _get_physics_prediction(self, example: TrainingExample) -> float:
        """Get prediction from physics-based model."""
        if self._chamber_model is None:
            # Fallback: simple heuristic based on ET dysfunction proxy
            worse_displacement = min(
                example.left_max_displacement,
                example.right_max_displacement,
            )
            # Lower displacement = higher risk
            return 1.0 - worse_displacement
        
        from .chamber_risk import ChamberScenario
        from .valsalva_video_analysis import (
            BilateralValsalvaResult,
            TMMovementFeatures,
            map_valsalva_to_et_dysfunction,
        )
        
        # Create mock Valsalva result from features
        left_features = TMMovementFeatures(
            max_displacement=example.left_max_displacement,
            response_latency=example.left_response_latency,
            movement_smoothness=example.left_movement_smoothness,
            movement_completeness=example.left_movement_completeness,
        )
        right_features = TMMovementFeatures(
            max_displacement=example.right_max_displacement,
            response_latency=example.right_response_latency,
            movement_smoothness=example.right_movement_smoothness,
            movement_completeness=example.right_movement_completeness,
        )
        
        valsalva_result = BilateralValsalvaResult(
            left_ear=left_features,
            right_ear=right_features,
            asymmetry_score=example.asymmetry_score,
        )
        
        et_score, severity = map_valsalva_to_et_dysfunction(valsalva_result)
        
        # Map to severity category
        if et_score < 0.4:
            et_severity = "mild"
        elif et_score < 0.7:
            et_severity = "moderate"
        else:
            et_severity = "severe"
        
        # Run chamber simulation
        scenario = ChamberScenario(
            start_altitude_ft=25000.0,
            descent_rate_ft_min=3000.0,
            et_severity=et_severity,
            enable_valsava=True,
        )
        
        result = self._chamber_model.simulate_descent(scenario)
        return result.risk_score
    
    def train(self, examples: List[TrainingExample]) -> ModelMetrics:
        """Train hybrid model."""
        # Train ML component
        ml_metrics = self._ml_model.train(examples)
        
        self.is_trained = True
        self._training_examples = examples.copy()
        
        return ml_metrics
    
    def predict_proba(self, example: TrainingExample) -> float:
        """Predict combined probability."""
        physics_pred = self._get_physics_prediction(example)
        
        if self.is_trained:
            ml_pred = self._ml_model.predict_proba(example)
        else:
            ml_pred = physics_pred  # Fallback to physics only
        
        # Weighted combination
        combined = (
            self.physics_weight * physics_pred +
            self.ml_weight * ml_pred
        )
        
        return float(np.clip(combined, 0.0, 1.0))
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from ML component."""
        if not self.is_trained:
            return {name: 0.0 for name in FEATURE_NAMES}
        return self._ml_model.get_feature_importance()
    
    def get_prediction_breakdown(self, example: TrainingExample) -> Dict[str, float]:
        """Get breakdown of physics vs ML contributions."""
        physics = self._get_physics_prediction(example)
        ml = self._ml_model.predict_proba(example) if self.is_trained else physics
        combined = self.predict_proba(example)
        
        return {
            'physics_prediction': physics,
            'physics_weighted': physics * self.physics_weight,
            'ml_prediction': ml,
            'ml_weighted': ml * self.ml_weight,
            'combined_prediction': combined,
        }
    
    def save(self, path: Path) -> None:
        """Save hybrid model."""
        ml_path = path.with_suffix('.ml.json')
        self._ml_model.save(ml_path)
        
        config = {
            'physics_weight': self.physics_weight,
            'ml_weight': self.ml_weight,
            'ml_model_path': str(ml_path),
        }
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load(self, path: Path) -> None:
        """Load hybrid model."""
        with open(path, 'r') as f:
            config = json.load(f)
        
        self.physics_weight = config['physics_weight']
        self.ml_weight = config['ml_weight']
        
        ml_path = Path(config['ml_model_path'])
        self._ml_model.load(ml_path)
        
        self.is_trained = True


# ============================================================================
# Model Factory
# ============================================================================

def create_model(
    model_type: str = "hybrid",
    **kwargs: Any,
) -> BarotraumaRiskModel:
    """
    Factory function to create barotrauma risk model.
    
    Args:
        model_type: "logistic", "gradient_boosting", or "hybrid"
        **kwargs: Model-specific parameters
        
    Returns:
        Instantiated model
    """
    if model_type == "logistic":
        return LogisticRegressionModel(**kwargs)
    elif model_type == "gradient_boosting":
        return GradientBoostingModel(**kwargs)
    elif model_type == "hybrid":
        return HybridPhysicsMLModel(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
