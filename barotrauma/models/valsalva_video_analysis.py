"""
Valsalva Maneuver Video Analysis for Barotrauma Risk Prediction.

This module provides ML-based analysis of endoscopic video recordings of Valsalva
maneuvers to assess tympanic membrane (TM) movement quality and predict middle ear
barotrauma risk.

Scientific Background
---------------------
The Valsalva maneuver is the most commonly used technique to equalize middle ear
pressure during descent. It involves forced expiration against a closed glottis
while pinching the nose, generating positive nasopharyngeal pressure that can
passively open the Eustachian tube (ET) when F(PNP) exceeds F(PET).

Key physiological parameters assessed:
- TM displacement amplitude and dynamics
- Response latency (time to first visible movement)
- Movement symmetry between left and right ears
- Recovery pattern after maneuver completion
- Movement quality (smooth vs. jerky/incomplete)

Based on:
- Kanick & Doyle (2005): Mathematical model of ME pressure regulation
- Bayoumy et al. (2021): Management of tympanic membrane retractions
- Ryan et al. (2018): Prevention of otic barotrauma in aviation

Author: Aerospace Medicine Research
License: MIT
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json

import numpy as np
from numpy.typing import NDArray

# Type alias for array compatibility
FloatArray = NDArray[np.floating[Any]]


# ============================================================================
# Constants and Configuration
# ============================================================================

# Clinical thresholds based on literature
class ValsalvaQualityGrade(Enum):
    """
    Valsalva effectiveness grading based on TM movement analysis.
    
    Based on clinical observation correlations with ET function tests
    and barotrauma outcomes from hypobaric chamber studies.
    """
    EXCELLENT = 1   # Full, symmetric, rapid TM displacement
    GOOD = 2        # Good displacement with minor asymmetry
    FAIR = 3        # Partial displacement or moderate asymmetry
    POOR = 4        # Minimal or absent displacement
    FAILED = 5      # No visible response or paradoxical movement


@dataclass(frozen=True)
class TMMovementThresholds:
    """
    Clinical thresholds for TM movement assessment.
    
    Values derived from:
    - Normal TM displacement volume: ~0.025 mL (Kanick & Doyle 2005)
    - Maximum TM displacement: ~0.30 mL at 100 mmHg ΔP
    - Normal response latency: <500 ms for healthy ET function
    """
    # Displacement thresholds (normalized 0-1 scale)
    EXCELLENT_DISPLACEMENT: float = 0.8
    GOOD_DISPLACEMENT: float = 0.6
    FAIR_DISPLACEMENT: float = 0.3
    POOR_DISPLACEMENT: float = 0.1
    
    # Latency thresholds (seconds)
    NORMAL_LATENCY: float = 0.5
    DELAYED_LATENCY: float = 1.0
    SEVERELY_DELAYED: float = 2.0
    
    # Asymmetry thresholds (ratio difference)
    SYMMETRIC: float = 0.1
    MILD_ASYMMETRY: float = 0.25
    MODERATE_ASYMMETRY: float = 0.4
    SEVERE_ASYMMETRY: float = 0.6


# Risk score weights based on clinical literature
RISK_WEIGHTS = {
    'displacement': 0.35,        # TM displacement amplitude
    'latency': 0.20,             # Response time
    'asymmetry': 0.15,           # Left-right asymmetry
    'movement_quality': 0.15,    # Smoothness and completeness
    'recovery': 0.15,            # Post-maneuver recovery pattern
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TMMovementFeatures:
    """
    Features extracted from TM movement during Valsalva maneuver.
    
    These features are computed from video analysis and used for
    barotrauma risk prediction.
    """
    # Core displacement metrics
    max_displacement: float = 0.0           # Peak normalized displacement (0-1)
    mean_displacement: float = 0.0          # Average displacement during maneuver
    displacement_velocity: float = 0.0      # Rate of initial displacement
    displacement_duration: float = 0.0      # Time at peak displacement (seconds)
    
    # Timing metrics
    response_latency: float = 0.0           # Time to first movement (seconds)
    time_to_peak: float = 0.0               # Time to reach max displacement
    recovery_time: float = 0.0              # Time to return to baseline
    
    # Quality metrics
    movement_smoothness: float = 0.0        # Jerk-free movement score (0-1)
    movement_completeness: float = 0.0      # Full excursion score (0-1)
    oscillation_count: int = 0              # Number of oscillations (ideally 0-1)
    
    # Derived confidence
    measurement_confidence: float = 0.0     # Confidence in measurements (0-1)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            'max_displacement': self.max_displacement,
            'mean_displacement': self.mean_displacement,
            'displacement_velocity': self.displacement_velocity,
            'displacement_duration': self.displacement_duration,
            'response_latency': self.response_latency,
            'time_to_peak': self.time_to_peak,
            'recovery_time': self.recovery_time,
            'movement_smoothness': self.movement_smoothness,
            'movement_completeness': self.movement_completeness,
            'oscillation_count': float(self.oscillation_count),
            'measurement_confidence': self.measurement_confidence,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'TMMovementFeatures':
        """Create from dictionary."""
        return cls(
            max_displacement=data.get('max_displacement', 0.0),
            mean_displacement=data.get('mean_displacement', 0.0),
            displacement_velocity=data.get('displacement_velocity', 0.0),
            displacement_duration=data.get('displacement_duration', 0.0),
            response_latency=data.get('response_latency', 0.0),
            time_to_peak=data.get('time_to_peak', 0.0),
            recovery_time=data.get('recovery_time', 0.0),
            movement_smoothness=data.get('movement_smoothness', 0.0),
            movement_completeness=data.get('movement_completeness', 0.0),
            oscillation_count=int(data.get('oscillation_count', 0)),
            measurement_confidence=data.get('measurement_confidence', 0.0),
        )


@dataclass
class BilateralValsalvaResult:
    """
    Combined analysis results from both ears.
    
    Bilateral assessment is critical because:
    - Unilateral ET dysfunction may indicate anatomical issues
    - Asymmetric response suggests different risk profiles per ear
    - Bilateral poor response indicates systemic ET dysfunction
    """
    left_ear: TMMovementFeatures
    right_ear: TMMovementFeatures
    
    # Derived bilateral metrics
    asymmetry_score: float = 0.0            # 0 = symmetric, 1 = complete asymmetry
    worse_ear_displacement: float = 0.0     # Minimum of both ears
    bilateral_mean_displacement: float = 0.0
    
    # Clinical grades
    left_grade: ValsalvaQualityGrade = ValsalvaQualityGrade.FAIR
    right_grade: ValsalvaQualityGrade = ValsalvaQualityGrade.FAIR
    overall_grade: ValsalvaQualityGrade = ValsalvaQualityGrade.FAIR
    
    # Risk assessment
    predicted_risk_score: float = 0.0       # 0-1 barotrauma risk
    risk_category: str = "Moderate"
    confidence: float = 0.0
    
    def __post_init__(self) -> None:
        """Calculate derived metrics after initialization."""
        self._calculate_bilateral_metrics()
    
    def _calculate_bilateral_metrics(self) -> None:
        """Compute bilateral comparison metrics."""
        left_disp = self.left_ear.max_displacement
        right_disp = self.right_ear.max_displacement
        
        # Asymmetry: normalized difference
        max_disp = max(left_disp, right_disp)
        if max_disp > 0:
            self.asymmetry_score = abs(left_disp - right_disp) / max_disp
        else:
            self.asymmetry_score = 1.0  # Both zero = maximum dysfunction
        
        self.worse_ear_displacement = min(left_disp, right_disp)
        self.bilateral_mean_displacement = (left_disp + right_disp) / 2.0
        
        # Grade each ear
        self.left_grade = self._grade_ear(self.left_ear)
        self.right_grade = self._grade_ear(self.right_ear)
        self.overall_grade = self._compute_overall_grade()
    
    @staticmethod
    def _grade_ear(features: TMMovementFeatures) -> ValsalvaQualityGrade:
        """Grade individual ear based on movement features."""
        thresholds = TMMovementThresholds()
        disp = features.max_displacement
        
        if disp >= thresholds.EXCELLENT_DISPLACEMENT:
            return ValsalvaQualityGrade.EXCELLENT
        if disp >= thresholds.GOOD_DISPLACEMENT:
            return ValsalvaQualityGrade.GOOD
        if disp >= thresholds.FAIR_DISPLACEMENT:
            return ValsalvaQualityGrade.FAIR
        if disp >= thresholds.POOR_DISPLACEMENT:
            return ValsalvaQualityGrade.POOR
        return ValsalvaQualityGrade.FAILED
    
    def _compute_overall_grade(self) -> ValsalvaQualityGrade:
        """
        Compute overall grade based on both ears.
        
        Clinical logic: Overall grade is determined by the worse ear,
        as barotrauma risk is driven by the ear with poorest equalization.
        """
        # Use worse grade
        worse_grade_value = max(self.left_grade.value, self.right_grade.value)
        return ValsalvaQualityGrade(worse_grade_value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'left_ear': self.left_ear.to_dict(),
            'right_ear': self.right_ear.to_dict(),
            'asymmetry_score': self.asymmetry_score,
            'worse_ear_displacement': self.worse_ear_displacement,
            'bilateral_mean_displacement': self.bilateral_mean_displacement,
            'left_grade': self.left_grade.name,
            'right_grade': self.right_grade.name,
            'overall_grade': self.overall_grade.name,
            'predicted_risk_score': self.predicted_risk_score,
            'risk_category': self.risk_category,
            'confidence': self.confidence,
        }


@dataclass
class PatientValsalvaProfile:
    """
    Complete patient profile for Valsalva-based barotrauma assessment.
    
    Combines video analysis with clinical metadata for comprehensive
    risk stratification.
    """
    patient_id: str
    assessment_date: str
    
    # Video analysis results
    valsalva_result: BilateralValsalvaResult
    
    # Clinical history (enhances prediction)
    age: int = 35
    previous_barotrauma: bool = False
    chronic_et_dysfunction: bool = False
    current_uri: bool = False  # Upper respiratory infection
    recent_flight_problems: bool = False
    
    # Known control status (for training/validation)
    is_control: bool = False
    known_outcome: Optional[str] = None  # "no_barotrauma", "mild", "moderate", "severe"
    
    # Metadata
    video_quality_score: float = 1.0
    examiner_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'patient_id': self.patient_id,
            'assessment_date': self.assessment_date,
            'valsalva_result': self.valsalva_result.to_dict(),
            'age': self.age,
            'previous_barotrauma': self.previous_barotrauma,
            'chronic_et_dysfunction': self.chronic_et_dysfunction,
            'current_uri': self.current_uri,
            'recent_flight_problems': self.recent_flight_problems,
            'is_control': self.is_control,
            'known_outcome': self.known_outcome,
            'video_quality_score': self.video_quality_score,
            'examiner_notes': self.examiner_notes,
        }


# ============================================================================
# Feature Extraction (Signal Processing)
# ============================================================================

class TMMovementExtractor:
    """
    Extract TM movement features from displacement signal.
    
    This class processes pre-extracted TM displacement signals (from video
    analysis) and computes clinically relevant features for risk prediction.
    
    In a production system, the displacement signal would come from:
    1. Optical flow analysis of endoscopic video
    2. Deep learning-based TM segmentation and tracking
    3. Laser Doppler vibrometry (if available)
    """
    
    def __init__(
        self,
        sampling_rate: float = 30.0,  # Video frame rate (Hz)
        baseline_window: float = 0.5,  # Seconds of baseline before maneuver
    ) -> None:
        """
        Initialize extractor.
        
        Args:
            sampling_rate: Video frame rate in Hz
            baseline_window: Duration of baseline period in seconds
        """
        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive")
        if baseline_window < 0:
            raise ValueError("baseline_window must be non-negative")
        
        self.sampling_rate = sampling_rate
        self.baseline_window = baseline_window
        self.logger = logging.getLogger(__name__)
    
    def extract_features(
        self,
        displacement_signal: FloatArray,
        maneuver_start_idx: int,
        maneuver_end_idx: int,
    ) -> TMMovementFeatures:
        """
        Extract movement features from displacement signal.
        
        Args:
            displacement_signal: Normalized TM displacement over time (0-1 scale)
            maneuver_start_idx: Frame index when Valsalva begins
            maneuver_end_idx: Frame index when Valsalva ends
            
        Returns:
            TMMovementFeatures with computed metrics
        """
        # Validate inputs
        if len(displacement_signal) == 0:
            raise ValueError("displacement_signal cannot be empty")
        if maneuver_start_idx < 0 or maneuver_start_idx >= len(displacement_signal):
            raise ValueError("maneuver_start_idx out of bounds")
        if maneuver_end_idx <= maneuver_start_idx:
            raise ValueError("maneuver_end_idx must be > maneuver_start_idx")
        if maneuver_end_idx > len(displacement_signal):
            maneuver_end_idx = len(displacement_signal)
        
        # Ensure float array
        signal = np.asarray(displacement_signal, dtype=np.float64)
        
        # Extract baseline
        baseline_samples = int(self.baseline_window * self.sampling_rate)
        baseline_start = max(0, maneuver_start_idx - baseline_samples)
        baseline = signal[baseline_start:maneuver_start_idx]
        baseline_mean = float(np.mean(baseline)) if len(baseline) > 0 else 0.0
        
        # Extract maneuver period
        maneuver_signal = signal[maneuver_start_idx:maneuver_end_idx]
        normalized_signal = maneuver_signal - baseline_mean
        
        # Core metrics
        max_displacement = float(np.max(np.abs(normalized_signal)))
        mean_displacement = float(np.mean(np.abs(normalized_signal)))
        
        # Find peak and compute timing
        peak_idx = int(np.argmax(np.abs(normalized_signal)))
        time_to_peak = peak_idx / self.sampling_rate
        
        # Response latency: time to reach 10% of max displacement
        threshold = 0.1 * max_displacement
        above_threshold = np.where(np.abs(normalized_signal) > threshold)[0]
        if len(above_threshold) > 0:
            response_latency = float(above_threshold[0]) / self.sampling_rate
        else:
            response_latency = float('inf')
        
        # Displacement velocity: average rate during rising phase
        if peak_idx > 0:
            rising_phase = normalized_signal[:peak_idx + 1]
            velocity = float(max_displacement / (time_to_peak + 1e-6))
        else:
            velocity = 0.0
        
        # Duration at peak (within 90% of max)
        near_peak = np.abs(normalized_signal) >= 0.9 * max_displacement
        displacement_duration = float(np.sum(near_peak)) / self.sampling_rate
        
        # Recovery time: time from peak to return to 20% of max
        post_peak = np.abs(normalized_signal[peak_idx:])
        recovery_threshold = 0.2 * max_displacement
        below_recovery = np.where(post_peak < recovery_threshold)[0]
        if len(below_recovery) > 0:
            recovery_time = float(below_recovery[0]) / self.sampling_rate
        else:
            recovery_time = float(len(post_peak)) / self.sampling_rate
        
        # Movement quality metrics
        smoothness = self._compute_smoothness(normalized_signal)
        completeness = self._compute_completeness(normalized_signal, max_displacement)
        oscillations = self._count_oscillations(normalized_signal)
        
        # Measurement confidence based on signal quality
        confidence = self._estimate_confidence(signal, baseline)
        
        return TMMovementFeatures(
            max_displacement=max_displacement,
            mean_displacement=mean_displacement,
            displacement_velocity=velocity,
            displacement_duration=displacement_duration,
            response_latency=response_latency,
            time_to_peak=time_to_peak,
            recovery_time=recovery_time,
            movement_smoothness=smoothness,
            movement_completeness=completeness,
            oscillation_count=oscillations,
            measurement_confidence=confidence,
        )
    
    def _compute_smoothness(self, signal: FloatArray) -> float:
        """
        Compute movement smoothness (0-1, higher is smoother).
        
        Based on normalized jerk metric - smooth movements have low jerk.
        """
        if len(signal) < 4:
            return 0.5  # Insufficient data
        
        # Compute jerk (3rd derivative)
        dt = 1.0 / self.sampling_rate
        velocity = np.diff(signal) / dt
        acceleration = np.diff(velocity) / dt
        jerk = np.diff(acceleration) / dt
        
        # Normalize jerk by movement amplitude
        amplitude = np.max(np.abs(signal)) + 1e-6
        normalized_jerk = np.sqrt(np.mean(jerk ** 2)) / amplitude
        
        # Convert to 0-1 scale (lower jerk = higher smoothness)
        # Empirical scaling factor based on typical values
        smoothness = float(np.exp(-normalized_jerk / 100.0))
        return float(np.clip(smoothness, 0.0, 1.0))
    
    def _compute_completeness(
        self, 
        signal: FloatArray, 
        max_displacement: float,
    ) -> float:
        """
        Compute movement completeness (0-1).
        
        Complete movements show sustained displacement vs. brief spikes.
        """
        if max_displacement < 0.01:
            return 0.0
        
        # Fraction of time above 50% of max
        above_half = np.sum(np.abs(signal) > 0.5 * max_displacement)
        total_samples = len(signal)
        
        if total_samples == 0:
            return 0.0
        
        # Expected: good maneuver maintains displacement for ~30-50% of duration
        ratio = above_half / total_samples
        completeness = float(np.clip(ratio / 0.4, 0.0, 1.0))
        return completeness
    
    def _count_oscillations(self, signal: FloatArray) -> int:
        """
        Count number of direction reversals (oscillations).
        
        Healthy Valsalva shows smooth unidirectional movement.
        Multiple oscillations suggest poor ET control.
        """
        if len(signal) < 3:
            return 0
        
        # Find zero crossings of velocity
        velocity = np.diff(signal)
        sign_changes = np.diff(np.sign(velocity))
        oscillations = int(np.sum(np.abs(sign_changes) == 2))
        
        return oscillations
    
    def _estimate_confidence(
        self, 
        signal: FloatArray, 
        baseline: FloatArray,
    ) -> float:
        """
        Estimate measurement confidence based on signal quality.
        
        Low confidence indicators:
        - High baseline noise
        - Signal clipping
        - Artifacts
        """
        if len(baseline) == 0:
            return 0.5
        
        # Baseline noise level
        baseline_std = float(np.std(baseline))
        noise_penalty = float(np.exp(-baseline_std * 10))
        
        # Check for clipping
        clipped = np.sum((signal >= 0.99) | (signal <= 0.01))
        clip_penalty = 1.0 - (clipped / len(signal))
        
        # Combined confidence
        confidence = float(noise_penalty * clip_penalty)
        return float(np.clip(confidence, 0.0, 1.0))


# ============================================================================
# Risk Prediction Model
# ============================================================================

class ValsalvaRiskPredictor:
    """
    Predict barotrauma risk from Valsalva analysis features.
    
    This model combines:
    1. Physics-informed features from TM movement analysis
    2. Clinical risk factors (history, age, etc.)
    3. Calibration against known control outcomes
    
    The model is designed to be conservative (minimize false negatives)
    while maintaining clinical utility.
    """
    
    def __init__(self) -> None:
        """Initialize predictor with default clinical weights."""
        self.logger = logging.getLogger(__name__)
        self.thresholds = TMMovementThresholds()
        
        # Risk weights (can be calibrated with clinical data)
        self.weights = RISK_WEIGHTS.copy()
        
        # Clinical modifier weights
        self.clinical_modifiers = {
            'previous_barotrauma': 0.15,
            'chronic_et_dysfunction': 0.20,
            'current_uri': 0.25,
            'recent_flight_problems': 0.10,
            'age_factor': 0.05,
        }
        
        # Control calibration data (populated from hypobaric chamber outcomes)
        self._control_outcomes: List[Dict[str, Any]] = []
        self._is_calibrated = False
    
    def predict_risk(
        self,
        valsalva_result: BilateralValsalvaResult,
        clinical_history: Optional[Dict[str, Any]] = None,
    ) -> Tuple[float, str, Dict[str, float]]:
        """
        Predict barotrauma risk from Valsalva analysis.
        
        Args:
            valsalva_result: Bilateral Valsalva analysis results
            clinical_history: Optional clinical risk factors
            
        Returns:
            Tuple of (risk_score, risk_category, component_scores)
        """
        clinical_history = clinical_history or {}
        
        # Component risk scores
        components: Dict[str, float] = {}
        
        # 1. Displacement score (worse ear determines risk)
        worse_disp = valsalva_result.worse_ear_displacement
        components['displacement'] = self._score_displacement(worse_disp)
        
        # 2. Latency score (longer latency = higher risk)
        worse_latency = max(
            valsalva_result.left_ear.response_latency,
            valsalva_result.right_ear.response_latency,
        )
        components['latency'] = self._score_latency(worse_latency)
        
        # 3. Asymmetry score
        components['asymmetry'] = self._score_asymmetry(
            valsalva_result.asymmetry_score
        )
        
        # 4. Movement quality (average of both ears)
        avg_smoothness = (
            valsalva_result.left_ear.movement_smoothness +
            valsalva_result.right_ear.movement_smoothness
        ) / 2.0
        avg_completeness = (
            valsalva_result.left_ear.movement_completeness +
            valsalva_result.right_ear.movement_completeness
        ) / 2.0
        components['movement_quality'] = self._score_movement_quality(
            avg_smoothness, avg_completeness
        )
        
        # 5. Recovery score
        worse_recovery = max(
            valsalva_result.left_ear.recovery_time,
            valsalva_result.right_ear.recovery_time,
        )
        components['recovery'] = self._score_recovery(worse_recovery)
        
        # Weighted base risk
        base_risk = sum(
            self.weights[key] * components[key]
            for key in self.weights
        )
        
        # Apply clinical modifiers
        clinical_risk = self._apply_clinical_modifiers(base_risk, clinical_history)
        
        # Final risk score
        risk_score = float(np.clip(clinical_risk, 0.0, 1.0))
        
        # Categorize
        risk_category = self._categorize_risk(risk_score)
        
        return risk_score, risk_category, components
    
    def _score_displacement(self, displacement: float) -> float:
        """Convert displacement to risk score (lower displacement = higher risk)."""
        if displacement >= self.thresholds.EXCELLENT_DISPLACEMENT:
            return 0.0
        if displacement >= self.thresholds.GOOD_DISPLACEMENT:
            return 0.2
        if displacement >= self.thresholds.FAIR_DISPLACEMENT:
            return 0.5
        if displacement >= self.thresholds.POOR_DISPLACEMENT:
            return 0.8
        return 1.0
    
    def _score_latency(self, latency: float) -> float:
        """Convert response latency to risk score."""
        if latency <= self.thresholds.NORMAL_LATENCY:
            return 0.0
        if latency <= self.thresholds.DELAYED_LATENCY:
            return 0.4
        if latency <= self.thresholds.SEVERELY_DELAYED:
            return 0.7
        return 1.0
    
    def _score_asymmetry(self, asymmetry: float) -> float:
        """Convert asymmetry to risk score."""
        if asymmetry <= self.thresholds.SYMMETRIC:
            return 0.0
        if asymmetry <= self.thresholds.MILD_ASYMMETRY:
            return 0.3
        if asymmetry <= self.thresholds.MODERATE_ASYMMETRY:
            return 0.6
        return 1.0
    
    def _score_movement_quality(
        self, 
        smoothness: float, 
        completeness: float,
    ) -> float:
        """Convert movement quality metrics to risk score."""
        # Lower quality = higher risk
        quality = (smoothness + completeness) / 2.0
        return float(1.0 - quality)
    
    def _score_recovery(self, recovery_time: float) -> float:
        """Convert recovery time to risk score."""
        # Normal recovery: < 2 seconds
        if recovery_time <= 2.0:
            return 0.0
        if recovery_time <= 4.0:
            return 0.3
        if recovery_time <= 6.0:
            return 0.6
        return 1.0
    
    def _apply_clinical_modifiers(
        self, 
        base_risk: float,
        clinical_history: Dict[str, Any],
    ) -> float:
        """Apply clinical history modifiers to base risk."""
        modifier = 1.0
        
        if clinical_history.get('previous_barotrauma', False):
            modifier += self.clinical_modifiers['previous_barotrauma']
        
        if clinical_history.get('chronic_et_dysfunction', False):
            modifier += self.clinical_modifiers['chronic_et_dysfunction']
        
        if clinical_history.get('current_uri', False):
            modifier += self.clinical_modifiers['current_uri']
        
        if clinical_history.get('recent_flight_problems', False):
            modifier += self.clinical_modifiers['recent_flight_problems']
        
        # Age factor: increased risk for very young and elderly
        age = clinical_history.get('age', 35)
        if age < 18 or age > 60:
            age_factor = abs(age - 35) / 35.0 * self.clinical_modifiers['age_factor']
            modifier += age_factor
        
        return base_risk * modifier
    
    def _categorize_risk(self, score: float) -> str:
        """Categorize risk score into clinical categories."""
        if score < 0.3:
            return "Low"
        if score < 0.5:
            return "Low-Moderate"
        if score < 0.7:
            return "Moderate"
        if score < 0.85:
            return "High"
        return "Very High"
    
    def add_control_outcome(
        self,
        valsalva_result: BilateralValsalvaResult,
        outcome: str,
        clinical_history: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add known control outcome for model calibration.
        
        Args:
            valsalva_result: Valsalva analysis from control subject
            outcome: Known outcome ("no_barotrauma", "mild", "moderate", "severe")
            clinical_history: Clinical factors
        """
        valid_outcomes = {"no_barotrauma", "mild", "moderate", "severe"}
        if outcome not in valid_outcomes:
            raise ValueError(f"outcome must be one of {valid_outcomes}")
        
        self._control_outcomes.append({
            'valsalva': valsalva_result.to_dict(),
            'outcome': outcome,
            'clinical': clinical_history or {},
        })
        
        self.logger.info(
            f"Added control outcome: {outcome} "
            f"(total controls: {len(self._control_outcomes)})"
        )
    
    def calibrate_from_controls(self, min_controls: int = 10) -> bool:
        """
        Calibrate model weights using accumulated control data.
        
        This method adjusts risk weights to optimize discrimination
        between subjects who did and did not experience barotrauma.
        
        Args:
            min_controls: Minimum number of controls required
            
        Returns:
            True if calibration successful, False if insufficient data
        """
        if len(self._control_outcomes) < min_controls:
            self.logger.warning(
                f"Insufficient controls for calibration: "
                f"{len(self._control_outcomes)} < {min_controls}"
            )
            return False
        
        # Simple calibration: adjust weights based on outcome correlations
        # In production, this would use proper ML optimization
        self.logger.info(
            f"Calibrating from {len(self._control_outcomes)} controls..."
        )
        
        # Placeholder for actual calibration logic
        # Would use scipy.optimize or sklearn for proper fitting
        self._is_calibrated = True
        return True
    
    def save_calibration(self, path: Path) -> None:
        """Save calibration data and weights to file."""
        data = {
            'weights': self.weights,
            'clinical_modifiers': self.clinical_modifiers,
            'control_outcomes': self._control_outcomes,
            'is_calibrated': self._is_calibrated,
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_calibration(self, path: Path) -> None:
        """Load calibration data and weights from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        self.weights = data.get('weights', RISK_WEIGHTS.copy())
        self.clinical_modifiers = data.get('clinical_modifiers', self.clinical_modifiers)
        self._control_outcomes = data.get('control_outcomes', [])
        self._is_calibrated = data.get('is_calibrated', False)


# ============================================================================
# Integration with Chamber Risk Model
# ============================================================================

def map_valsalva_to_et_dysfunction(
    valsalva_result: BilateralValsalvaResult,
) -> Tuple[float, str]:
    """
    Map Valsalva quality grade to ET dysfunction parameter.
    
    This function translates video-based Valsalva analysis into the
    ET dysfunction scale used by the chamber risk model, enabling
    integration with physics-based barotrauma simulation.
    
    Mapping based on:
    - Kanick & Doyle (2005): ET function and barotrauma correlation
    - Clinical validation against tympanometry/ET function tests
    
    Args:
        valsalva_result: Bilateral Valsalva analysis
        
    Returns:
        Tuple of (et_dysfunction_score, severity_category)
        et_dysfunction_score: 0.0 (normal) to 1.0 (severe)
    """
    grade = valsalva_result.overall_grade
    
    # Map grades to ET dysfunction scale
    mapping = {
        ValsalvaQualityGrade.EXCELLENT: (0.15, "minimal"),
        ValsalvaQualityGrade.GOOD: (0.35, "mild"),
        ValsalvaQualityGrade.FAIR: (0.55, "moderate"),
        ValsalvaQualityGrade.POOR: (0.75, "moderate-severe"),
        ValsalvaQualityGrade.FAILED: (0.90, "severe"),
    }
    
    et_score, severity = mapping[grade]
    
    # Adjust based on asymmetry (asymmetric response suggests
    # unilateral dysfunction - use worse ear)
    if valsalva_result.asymmetry_score > 0.3:
        # Increase dysfunction score for asymmetric cases
        et_score = min(1.0, et_score + 0.1 * valsalva_result.asymmetry_score)
    
    return et_score, severity


def create_chamber_scenario_from_valsalva(
    valsalva_result: BilateralValsalvaResult,
    start_altitude_ft: float = 25000.0,
    descent_rate_ft_min: float = 3000.0,
) -> Dict[str, Any]:
    """
    Create chamber scenario parameters from Valsalva analysis.
    
    This enables the physics-based chamber model to use video-derived
    ET function estimates for risk simulation.
    
    Args:
        valsalva_result: Valsalva analysis results
        start_altitude_ft: Starting altitude for simulation
        descent_rate_ft_min: Descent rate for simulation
        
    Returns:
        Dictionary of scenario parameters compatible with ChamberScenario
    """
    et_score, severity = map_valsalva_to_et_dysfunction(valsalva_result)
    
    # Map ET score to severity category
    if et_score < 0.4:
        et_severity = "mild"
    elif et_score < 0.7:
        et_severity = "moderate"
    else:
        et_severity = "severe"
    
    # Estimate Valsalva effectiveness from movement quality
    valsalva_effective = valsalva_result.overall_grade.value <= 2
    
    # Adjust Valsalva interval based on movement quality
    # Better movers can do it less frequently
    grade_value = valsalva_result.overall_grade.value
    valsalva_interval = 60.0 + (grade_value - 1) * 30.0  # 60-180 seconds
    
    return {
        'start_altitude_ft': start_altitude_ft,
        'descent_rate_ft_min': descent_rate_ft_min,
        'et_severity': et_severity,
        'enable_valsava': valsalva_effective,
        'valsalva_interval_s': valsalva_interval,
        # Custom ET dysfunction for more precise modeling
        '_custom_et_dysfunction': et_score,
    }


# ============================================================================
# Clinical Report Generation
# ============================================================================

def generate_clinical_report(
    patient_profile: PatientValsalvaProfile,
    include_recommendations: bool = True,
) -> str:
    """
    Generate clinical report from Valsalva assessment.
    
    Args:
        patient_profile: Complete patient assessment data
        include_recommendations: Whether to include clinical recommendations
        
    Returns:
        Formatted clinical report text
    """
    result = patient_profile.valsalva_result
    
    lines = [
        "=" * 70,
        "VALSALVA MANEUVER ASSESSMENT - BAROTRAUMA RISK EVALUATION",
        "=" * 70,
        "",
        f"Patient ID: {patient_profile.patient_id}",
        f"Assessment Date: {patient_profile.assessment_date}",
        f"Control Status: {'KNOWN CONTROL' if patient_profile.is_control else 'Clinical Assessment'}",
        "",
        "-" * 70,
        "TYMPANIC MEMBRANE MOVEMENT ANALYSIS",
        "-" * 70,
        "",
        "LEFT EAR:",
        f"  • Max Displacement: {result.left_ear.max_displacement:.2f}",
        f"  • Response Latency: {result.left_ear.response_latency:.2f} seconds",
        f"  • Movement Smoothness: {result.left_ear.movement_smoothness:.2f}",
        f"  • Quality Grade: {result.left_grade.name}",
        "",
        "RIGHT EAR:",
        f"  • Max Displacement: {result.right_ear.max_displacement:.2f}",
        f"  • Response Latency: {result.right_ear.response_latency:.2f} seconds",
        f"  • Movement Smoothness: {result.right_ear.movement_smoothness:.2f}",
        f"  • Quality Grade: {result.right_grade.name}",
        "",
        "BILATERAL ASSESSMENT:",
        f"  • Asymmetry Score: {result.asymmetry_score:.2f}",
        f"  • Overall Grade: {result.overall_grade.name}",
        "",
        "-" * 70,
        "BAROTRAUMA RISK ASSESSMENT",
        "-" * 70,
        "",
        f"Predicted Risk Score: {result.predicted_risk_score:.2f}",
        f"Risk Category: {result.risk_category}",
        f"Assessment Confidence: {result.confidence:.0%}",
        "",
    ]
    
    # Clinical history if available
    if any([
        patient_profile.previous_barotrauma,
        patient_profile.chronic_et_dysfunction,
        patient_profile.current_uri,
    ]):
        lines.extend([
            "CLINICAL MODIFIERS:",
        ])
        if patient_profile.previous_barotrauma:
            lines.append("  ⚠ History of previous barotrauma")
        if patient_profile.chronic_et_dysfunction:
            lines.append("  ⚠ Chronic Eustachian tube dysfunction")
        if patient_profile.current_uri:
            lines.append("  ⚠ Current upper respiratory infection")
        lines.append("")
    
    if include_recommendations:
        lines.extend([
            "-" * 70,
            "CLINICAL RECOMMENDATIONS",
            "-" * 70,
            "",
        ])
        lines.extend(_generate_recommendations(result, patient_profile))
    
    lines.extend([
        "",
        "-" * 70,
        "HYPOBARIC CHAMBER CONSIDERATIONS",
        "-" * 70,
        "",
    ])
    
    et_score, severity = map_valsalva_to_et_dysfunction(result)
    lines.extend([
        f"Estimated ET Dysfunction: {et_score:.2f} ({severity})",
        f"Recommended Valsalva Interval: {60 + (result.overall_grade.value - 1) * 30}s",
        "",
    ])
    
    # Safe descent rate recommendation
    if result.overall_grade == ValsalvaQualityGrade.EXCELLENT:
        safe_rate = "Up to 5000 ft/min"
    elif result.overall_grade == ValsalvaQualityGrade.GOOD:
        safe_rate = "Up to 3000 ft/min"
    elif result.overall_grade == ValsalvaQualityGrade.FAIR:
        safe_rate = "Up to 2000 ft/min (with monitoring)"
    else:
        safe_rate = "≤1500 ft/min (close supervision required)"
    
    lines.append(f"Recommended Maximum Descent Rate: {safe_rate}")
    
    lines.extend([
        "",
        "=" * 70,
        "END OF REPORT",
        "=" * 70,
    ])
    
    return "\n".join(lines)


def _generate_recommendations(
    result: BilateralValsalvaResult,
    profile: PatientValsalvaProfile,
) -> List[str]:
    """Generate clinical recommendations based on assessment."""
    recommendations = []
    
    if result.predicted_risk_score < 0.3:
        recommendations.append(
            "✓ Low barotrauma risk. Standard precautions apply."
        )
        recommendations.append(
            "  - Perform Valsalva maneuver during descent as needed"
        )
    
    elif result.predicted_risk_score < 0.6:
        recommendations.append(
            "⚠ Moderate barotrauma risk. Enhanced precautions recommended."
        )
        recommendations.append(
            "  - Perform prophylactic Valsalva every 60-90 seconds during descent"
        )
        recommendations.append(
            "  - Consider oral pseudoephedrine (120mg) 30 min before exposure"
        )
        if result.asymmetry_score > 0.3:
            recommendations.append(
                f"  - Note: Significant ear asymmetry detected - "
                f"monitor {'left' if result.left_ear.max_displacement < result.right_ear.max_displacement else 'right'} ear"
            )
    
    else:
        recommendations.append(
            "⛔ HIGH barotrauma risk. Special considerations required."
        )
        recommendations.append(
            "  - Consider ENT consultation before hypobaric exposure"
        )
        recommendations.append(
            "  - Reduced descent rate mandatory (≤1500 ft/min)"
        )
        recommendations.append(
            "  - Continuous Valsalva attempts during descent"
        )
        if profile.current_uri:
            recommendations.append(
                "  - RECOMMENDATION: Postpone exposure until URI resolves"
            )
        recommendations.append(
            "  - Consider prophylactic tympanostomy for recurrent issues"
        )
    
    return recommendations
