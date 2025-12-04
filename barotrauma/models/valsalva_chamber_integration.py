"""
Integration of Valsalva Video Analysis with Chamber Risk Model.

This module provides the glue between:
1. Video-based Valsalva maneuver analysis
2. Physics-based hypobaric chamber simulation
3. ML-based risk prediction

The integration enables:
- Personalized risk prediction using patient-specific ET function
- Simulation of chamber scenarios with video-derived parameters
- Clinical decision support for hypobaric chamber operations

Author: Aerospace Medicine Research
License: MIT
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .chamber_risk import (
    HypobaricChamberRiskModel,
    ChamberScenario,
    ChamberResult,
)
from .valsalva_video_analysis import (
    BilateralValsalvaResult,
    TMMovementFeatures,
    TMMovementExtractor,
    ValsalvaRiskPredictor,
    PatientValsalvaProfile,
    ValsalvaQualityGrade,
    map_valsalva_to_et_dysfunction,
    create_chamber_scenario_from_valsalva,
    generate_clinical_report,
)
from .ml_risk_model import (
    BarotraumaRiskModel,
    TrainingExample,
    LogisticRegressionModel,
    HybridPhysicsMLModel,
    create_model,
)


# ============================================================================
# Integrated Assessment System
# ============================================================================

@dataclass
class IntegratedRiskAssessment:
    """
    Complete integrated risk assessment combining all analysis methods.
    
    This represents the final output of the clinical decision support system.
    """
    # Patient identification
    patient_id: str
    assessment_date: str
    
    # Valsalva video analysis results
    valsalva_result: BilateralValsalvaResult
    valsalva_quality_grade: str
    
    # Physics-based simulation results
    chamber_simulation: Optional[ChamberResult]
    simulated_max_delta_p: float
    simulated_risk_score: float
    
    # ML model prediction
    ml_risk_probability: float
    ml_risk_category: str
    ml_confidence: float
    
    # Integrated prediction
    final_risk_score: float
    final_risk_category: str
    
    # Clinical recommendations
    recommendations: List[str]
    contraindications: List[str]
    
    # Safe operational parameters
    recommended_max_descent_rate: float
    recommended_valsalva_interval: float
    requires_enhanced_monitoring: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'patient_id': self.patient_id,
            'assessment_date': self.assessment_date,
            'valsalva_result': self.valsalva_result.to_dict(),
            'valsalva_quality_grade': self.valsalva_quality_grade,
            'simulated_max_delta_p': self.simulated_max_delta_p,
            'simulated_risk_score': self.simulated_risk_score,
            'ml_risk_probability': self.ml_risk_probability,
            'ml_risk_category': self.ml_risk_category,
            'ml_confidence': self.ml_confidence,
            'final_risk_score': self.final_risk_score,
            'final_risk_category': self.final_risk_category,
            'recommendations': self.recommendations,
            'contraindications': self.contraindications,
            'recommended_max_descent_rate': self.recommended_max_descent_rate,
            'recommended_valsalva_interval': self.recommended_valsalva_interval,
            'requires_enhanced_monitoring': self.requires_enhanced_monitoring,
        }


class IntegratedBarotraumaAssessment:
    """
    Integrated system for barotrauma risk assessment.
    
    Combines:
    - Video-based Valsalva analysis
    - Physics-based chamber simulation
    - ML risk prediction
    - Clinical decision support
    
    This is the main entry point for the clinical assessment workflow.
    """
    
    def __init__(
        self,
        ml_model: Optional[BarotraumaRiskModel] = None,
        use_hybrid_model: bool = True,
    ) -> None:
        """
        Initialize integrated assessment system.
        
        Args:
            ml_model: Pre-trained ML model (optional)
            use_hybrid_model: Whether to use hybrid physics+ML model
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.chamber_model = HypobaricChamberRiskModel()
        self.valsalva_predictor = ValsalvaRiskPredictor()
        self.feature_extractor = TMMovementExtractor()
        
        # ML model
        if ml_model is not None:
            self.ml_model = ml_model
        elif use_hybrid_model:
            self.ml_model = HybridPhysicsMLModel()
        else:
            self.ml_model = LogisticRegressionModel()
        
        # Control data for calibration
        self._control_database: List[Dict[str, Any]] = []
    
    def assess_from_valsalva(
        self,
        valsalva_result: BilateralValsalvaResult,
        patient_id: str,
        clinical_history: Optional[Dict[str, Any]] = None,
        chamber_altitude_ft: float = 25000.0,
        chamber_descent_rate: float = 3000.0,
    ) -> IntegratedRiskAssessment:
        """
        Perform complete integrated assessment from Valsalva results.
        
        Args:
            valsalva_result: Analyzed Valsalva maneuver data
            patient_id: Patient identifier
            clinical_history: Clinical history dict
            chamber_altitude_ft: Target altitude for chamber simulation
            chamber_descent_rate: Descent rate for simulation
            
        Returns:
            IntegratedRiskAssessment with all predictions and recommendations
        """
        clinical_history = clinical_history or {}
        assessment_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 1. Map Valsalva to ET dysfunction for simulation
        scenario_params = create_chamber_scenario_from_valsalva(
            valsalva_result,
            start_altitude_ft=chamber_altitude_ft,
            descent_rate_ft_min=chamber_descent_rate,
        )
        
        # 2. Run physics-based chamber simulation
        scenario = ChamberScenario(
            start_altitude_ft=scenario_params['start_altitude_ft'],
            descent_rate_ft_min=scenario_params['descent_rate_ft_min'],
            et_severity=scenario_params['et_severity'],
            enable_valsava=scenario_params['enable_valsava'],
            valsalva_interval_s=scenario_params['valsalva_interval_s'],
        )
        
        chamber_result = self.chamber_model.simulate_descent(scenario)
        
        # 3. Valsalva-based risk prediction
        valsalva_score, valsalva_category, components = self.valsalva_predictor.predict_risk(
            valsalva_result, clinical_history
        )
        
        # Update valsalva_result with prediction
        valsalva_result.predicted_risk_score = valsalva_score
        valsalva_result.risk_category = valsalva_category
        valsalva_result.confidence = self._estimate_confidence(valsalva_result)
        
        # 4. ML prediction (if trained)
        ml_probability = 0.5
        ml_category = "Unknown"
        ml_confidence = 0.0
        
        if self.ml_model.is_trained:
            example = self._valsalva_to_training_example(
                valsalva_result, clinical_history, patient_id
            )
            ml_probability = self.ml_model.predict_proba(example)
            ml_category = self.ml_model.predict(example)
            ml_confidence = 0.8  # Placeholder - would compute from model calibration
        
        # 5. Combine predictions
        final_score, final_category = self._combine_predictions(
            chamber_result.risk_score,
            valsalva_score,
            ml_probability,
        )
        
        # 6. Generate recommendations
        recommendations = self._generate_recommendations(
            valsalva_result, chamber_result, final_score, clinical_history
        )
        contraindications = self._check_contraindications(
            valsalva_result, clinical_history
        )
        
        # 7. Compute safe operational parameters
        max_descent_rate = self._compute_safe_descent_rate(
            valsalva_result, chamber_result
        )
        valsalva_interval = scenario_params['valsalva_interval_s']
        enhanced_monitoring = final_score > 0.5
        
        return IntegratedRiskAssessment(
            patient_id=patient_id,
            assessment_date=assessment_date,
            valsalva_result=valsalva_result,
            valsalva_quality_grade=valsalva_result.overall_grade.name,
            chamber_simulation=chamber_result,
            simulated_max_delta_p=float(np.max(np.abs(chamber_result.delta_P_mmHg))),
            simulated_risk_score=chamber_result.risk_score,
            ml_risk_probability=ml_probability,
            ml_risk_category=ml_category,
            ml_confidence=ml_confidence,
            final_risk_score=final_score,
            final_risk_category=final_category,
            recommendations=recommendations,
            contraindications=contraindications,
            recommended_max_descent_rate=max_descent_rate,
            recommended_valsalva_interval=valsalva_interval,
            requires_enhanced_monitoring=enhanced_monitoring,
        )
    
    def assess_from_displacement_signals(
        self,
        left_signal: np.ndarray,
        right_signal: np.ndarray,
        sampling_rate: float,
        left_maneuver_indices: Tuple[int, int],
        right_maneuver_indices: Tuple[int, int],
        patient_id: str,
        clinical_history: Optional[Dict[str, Any]] = None,
        **chamber_kwargs: Any,
    ) -> IntegratedRiskAssessment:
        """
        Perform assessment from raw displacement signals.
        
        This is the entry point when video has already been processed
        to displacement signals.
        
        Args:
            left_signal: Left ear displacement signal (normalized 0-1)
            right_signal: Right ear displacement signal (normalized 0-1)
            sampling_rate: Sampling rate in Hz
            left_maneuver_indices: (start_idx, end_idx) for left ear
            right_maneuver_indices: (start_idx, end_idx) for right ear
            patient_id: Patient identifier
            clinical_history: Clinical history dict
            **chamber_kwargs: Additional chamber scenario parameters
            
        Returns:
            IntegratedRiskAssessment
        """
        # Extract features from signals
        extractor = TMMovementExtractor(sampling_rate=sampling_rate)
        
        left_features = extractor.extract_features(
            left_signal,
            left_maneuver_indices[0],
            left_maneuver_indices[1],
        )
        right_features = extractor.extract_features(
            right_signal,
            right_maneuver_indices[0],
            right_maneuver_indices[1],
        )
        
        # Create bilateral result
        valsalva_result = BilateralValsalvaResult(
            left_ear=left_features,
            right_ear=right_features,
        )
        
        return self.assess_from_valsalva(
            valsalva_result=valsalva_result,
            patient_id=patient_id,
            clinical_history=clinical_history,
            **chamber_kwargs,
        )
    
    def add_control_outcome(
        self,
        assessment: IntegratedRiskAssessment,
        actual_outcome: str,
    ) -> None:
        """
        Add known control outcome for model training/calibration.
        
        Call this after hypobaric chamber exposure when the actual
        outcome is known.
        
        Args:
            assessment: The pre-exposure assessment
            actual_outcome: "no_barotrauma", "mild", "moderate", or "severe"
        """
        valid_outcomes = {"no_barotrauma", "mild", "moderate", "severe"}
        if actual_outcome not in valid_outcomes:
            raise ValueError(f"outcome must be one of {valid_outcomes}")
        
        # Store in control database
        control_record = {
            'assessment': assessment.to_dict(),
            'actual_outcome': actual_outcome,
            'recorded_at': datetime.now().isoformat(),
        }
        self._control_database.append(control_record)
        
        # Add to Valsalva predictor
        self.valsalva_predictor.add_control_outcome(
            assessment.valsalva_result,
            actual_outcome,
        )
        
        # Add to ML model training data
        clinical_history = {
            'age': 35,  # Would extract from assessment
            'previous_barotrauma': False,
            'chronic_et_dysfunction': False,
            'current_uri': False,
        }
        
        example = self._valsalva_to_training_example(
            assessment.valsalva_result,
            clinical_history,
            assessment.patient_id,
            outcome=actual_outcome,
            is_control=True,
        )
        self.ml_model.add_training_example(example)
        
        self.logger.info(
            f"Added control outcome: {actual_outcome} "
            f"(total controls: {len(self._control_database)})"
        )
    
    def train_ml_model(self, min_controls: int = 20) -> bool:
        """
        Train/retrain ML model from accumulated control data.
        
        Args:
            min_controls: Minimum controls required for training
            
        Returns:
            True if training successful
        """
        if len(self._control_database) < min_controls:
            self.logger.warning(
                f"Insufficient controls: {len(self._control_database)} < {min_controls}"
            )
            return False
        
        # Convert controls to training examples
        examples = []
        for record in self._control_database:
            assessment = record['assessment']
            outcome = record['actual_outcome']
            
            # Reconstruct valsalva result from dict
            valsalva_dict = assessment['valsalva_result']
            left_features = TMMovementFeatures.from_dict(valsalva_dict['left_ear'])
            right_features = TMMovementFeatures.from_dict(valsalva_dict['right_ear'])
            
            example = TrainingExample(
                left_max_displacement=left_features.max_displacement,
                left_response_latency=left_features.response_latency,
                left_movement_smoothness=left_features.movement_smoothness,
                left_movement_completeness=left_features.movement_completeness,
                right_max_displacement=right_features.max_displacement,
                right_response_latency=right_features.response_latency,
                right_movement_smoothness=right_features.movement_smoothness,
                right_movement_completeness=right_features.movement_completeness,
                asymmetry_score=valsalva_dict['asymmetry_score'],
                age=35,
                previous_barotrauma=False,
                chronic_et_dysfunction=False,
                current_uri=False,
                outcome=outcome,
                patient_id=assessment['patient_id'],
                is_control=True,
            )
            examples.append(example)
        
        # Train model
        metrics = self.ml_model.train(examples)
        
        self.logger.info(
            f"ML model trained on {len(examples)} controls. "
            f"AUC: {metrics.auc_roc:.3f}, Brier: {metrics.brier_score:.3f}"
        )
        
        return True
    
    def save_state(self, directory: Path) -> None:
        """
        Save all model state including control database.
        
        Args:
            directory: Directory to save state files
        """
        import json
        
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        
        # Save control database
        controls_path = directory / "control_database.json"
        with open(controls_path, 'w') as f:
            json.dump(self._control_database, f, indent=2)
        
        # Save ML model if trained
        if self.ml_model.is_trained:
            model_path = directory / "ml_model.json"
            self.ml_model.save(model_path)
        
        # Save Valsalva predictor calibration
        predictor_path = directory / "valsalva_predictor.json"
        self.valsalva_predictor.save_calibration(predictor_path)
        
        self.logger.info(f"State saved to {directory}")
    
    def load_state(self, directory: Path) -> None:
        """
        Load model state from directory.
        
        Args:
            directory: Directory containing state files
        """
        import json
        
        directory = Path(directory)
        
        # Load control database
        controls_path = directory / "control_database.json"
        if controls_path.exists():
            with open(controls_path, 'r') as f:
                self._control_database = json.load(f)
        
        # Load ML model
        model_path = directory / "ml_model.json"
        if model_path.exists():
            self.ml_model.load(model_path)
        
        # Load Valsalva predictor calibration
        predictor_path = directory / "valsalva_predictor.json"
        if predictor_path.exists():
            self.valsalva_predictor.load_calibration(predictor_path)
        
        self.logger.info(f"State loaded from {directory}")
    
    def _estimate_confidence(
        self,
        valsalva_result: BilateralValsalvaResult,
    ) -> float:
        """Estimate overall confidence in assessment."""
        left_conf = valsalva_result.left_ear.measurement_confidence
        right_conf = valsalva_result.right_ear.measurement_confidence
        
        # Lower confidence if asymmetric (may indicate unilateral issue)
        asymmetry_penalty = 1.0 - 0.3 * valsalva_result.asymmetry_score
        
        return float((left_conf + right_conf) / 2.0 * asymmetry_penalty)
    
    def _valsalva_to_training_example(
        self,
        valsalva_result: BilateralValsalvaResult,
        clinical_history: Dict[str, Any],
        patient_id: str,
        outcome: str = "unknown",
        is_control: bool = False,
    ) -> TrainingExample:
        """Convert Valsalva result to TrainingExample."""
        return TrainingExample(
            left_max_displacement=valsalva_result.left_ear.max_displacement,
            left_response_latency=valsalva_result.left_ear.response_latency,
            left_movement_smoothness=valsalva_result.left_ear.movement_smoothness,
            left_movement_completeness=valsalva_result.left_ear.movement_completeness,
            right_max_displacement=valsalva_result.right_ear.max_displacement,
            right_response_latency=valsalva_result.right_ear.response_latency,
            right_movement_smoothness=valsalva_result.right_ear.movement_smoothness,
            right_movement_completeness=valsalva_result.right_ear.movement_completeness,
            asymmetry_score=valsalva_result.asymmetry_score,
            age=clinical_history.get('age', 35),
            previous_barotrauma=clinical_history.get('previous_barotrauma', False),
            chronic_et_dysfunction=clinical_history.get('chronic_et_dysfunction', False),
            current_uri=clinical_history.get('current_uri', False),
            outcome=outcome,
            patient_id=patient_id,
            is_control=is_control,
        )
    
    def _combine_predictions(
        self,
        chamber_score: float,
        valsalva_score: float,
        ml_probability: float,
    ) -> Tuple[float, str]:
        """Combine predictions from different models."""
        # Weighted average with emphasis on physics model
        if self.ml_model.is_trained:
            weights = [0.3, 0.3, 0.4]  # chamber, valsalva, ML
            combined = (
                weights[0] * chamber_score +
                weights[1] * valsalva_score +
                weights[2] * ml_probability
            )
        else:
            weights = [0.5, 0.5]  # chamber, valsalva only
            combined = weights[0] * chamber_score + weights[1] * valsalva_score
        
        combined = float(np.clip(combined, 0.0, 1.0))
        
        # Categorize
        if combined < 0.25:
            category = "Low"
        elif combined < 0.45:
            category = "Low-Moderate"
        elif combined < 0.65:
            category = "Moderate"
        elif combined < 0.80:
            category = "High"
        else:
            category = "Very High"
        
        return combined, category
    
    def _generate_recommendations(
        self,
        valsalva_result: BilateralValsalvaResult,
        chamber_result: ChamberResult,
        final_score: float,
        clinical_history: Dict[str, Any],
    ) -> List[str]:
        """Generate clinical recommendations."""
        recommendations = []
        
        # Risk-based recommendations
        if final_score < 0.3:
            recommendations.append(
                "✓ Low risk - standard hypobaric chamber protocol appropriate"
            )
        elif final_score < 0.6:
            recommendations.extend([
                "⚠ Moderate risk - enhanced monitoring recommended",
                "- Perform Valsalva every 60-90 seconds during descent",
                "- Consider slower descent rate (≤2500 ft/min)",
            ])
        else:
            recommendations.extend([
                "⛔ HIGH RISK - special precautions required",
                "- Reduced descent rate (≤1500 ft/min) mandatory",
                "- Continuous Valsalva attempts during descent",
                "- Consider medical officer presence during exposure",
            ])
        
        # Valsalva-specific recommendations
        grade = valsalva_result.overall_grade
        if grade in (ValsalvaQualityGrade.POOR, ValsalvaQualityGrade.FAILED):
            recommendations.append(
                "- Valsalva technique review recommended before exposure"
            )
        
        if valsalva_result.asymmetry_score > 0.3:
            worse_ear = (
                "left" if valsalva_result.left_ear.max_displacement <
                valsalva_result.right_ear.max_displacement else "right"
            )
            recommendations.append(
                f"- Significant asymmetry: monitor {worse_ear} ear closely"
            )
        
        # Clinical history-based
        if clinical_history.get('current_uri', False):
            recommendations.append(
                "- CONSIDER: Postpone exposure until URI symptoms resolve"
            )
        
        if clinical_history.get('previous_barotrauma', False):
            recommendations.append(
                "- History of barotrauma: lower threshold for abort"
            )
        
        return recommendations
    
    def _check_contraindications(
        self,
        valsalva_result: BilateralValsalvaResult,
        clinical_history: Dict[str, Any],
    ) -> List[str]:
        """Check for contraindications to hypobaric exposure."""
        contraindications = []
        
        # Absolute contraindications
        if valsalva_result.overall_grade == ValsalvaQualityGrade.FAILED:
            if valsalva_result.worse_ear_displacement < 0.05:
                contraindications.append(
                    "ABSOLUTE: Unable to demonstrate any Valsalva response"
                )
        
        if clinical_history.get('acute_otitis_media', False):
            contraindications.append(
                "ABSOLUTE: Active middle ear infection"
            )
        
        # Relative contraindications
        if clinical_history.get('current_uri', False):
            contraindications.append(
                "RELATIVE: Active upper respiratory infection"
            )
        
        if clinical_history.get('previous_barotrauma', False) and \
           valsalva_result.overall_grade.value >= 4:
            contraindications.append(
                "RELATIVE: History of barotrauma with poor current function"
            )
        
        return contraindications
    
    def _compute_safe_descent_rate(
        self,
        valsalva_result: BilateralValsalvaResult,
        chamber_result: ChamberResult,
    ) -> float:
        """Compute recommended maximum descent rate."""
        grade = valsalva_result.overall_grade
        
        # Base rates by Valsalva grade
        base_rates = {
            ValsalvaQualityGrade.EXCELLENT: 6000.0,
            ValsalvaQualityGrade.GOOD: 4000.0,
            ValsalvaQualityGrade.FAIR: 2500.0,
            ValsalvaQualityGrade.POOR: 1500.0,
            ValsalvaQualityGrade.FAILED: 1000.0,
        }
        
        base_rate = base_rates[grade]
        
        # Adjust based on simulation results
        max_dp = float(np.max(np.abs(chamber_result.delta_P_mmHg)))
        if max_dp > 90:  # ET lock threshold
            base_rate *= 0.7
        elif max_dp > 60:
            base_rate *= 0.85
        
        # Ensure within valid range
        return float(np.clip(base_rate, 1000.0, 10000.0))


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_assess(
    left_displacement: float,
    right_displacement: float,
    left_latency: float = 0.5,
    right_latency: float = 0.5,
    asymmetry: Optional[float] = None,
    patient_id: str = "anonymous",
) -> IntegratedRiskAssessment:
    """
    Quick assessment from summary displacement metrics.
    
    This is a convenience function for rapid screening when
    full video analysis is not available.
    
    Args:
        left_displacement: Left ear max displacement (0-1)
        right_displacement: Right ear max displacement (0-1)
        left_latency: Left ear response latency (seconds)
        right_latency: Right ear response latency (seconds)
        asymmetry: Asymmetry score (computed if None)
        patient_id: Patient identifier
        
    Returns:
        IntegratedRiskAssessment
    """
    # Create minimal feature sets
    left_features = TMMovementFeatures(
        max_displacement=left_displacement,
        mean_displacement=left_displacement * 0.6,
        response_latency=left_latency,
        movement_smoothness=0.7,
        movement_completeness=0.7,
        measurement_confidence=0.8,
    )
    
    right_features = TMMovementFeatures(
        max_displacement=right_displacement,
        mean_displacement=right_displacement * 0.6,
        response_latency=right_latency,
        movement_smoothness=0.7,
        movement_completeness=0.7,
        measurement_confidence=0.8,
    )
    
    if asymmetry is None:
        max_disp = max(left_displacement, right_displacement)
        if max_disp > 0:
            asymmetry = abs(left_displacement - right_displacement) / max_disp
        else:
            asymmetry = 1.0
    
    valsalva_result = BilateralValsalvaResult(
        left_ear=left_features,
        right_ear=right_features,
        asymmetry_score=asymmetry,
    )
    
    # Run assessment
    system = IntegratedBarotraumaAssessment()
    return system.assess_from_valsalva(
        valsalva_result=valsalva_result,
        patient_id=patient_id,
    )
