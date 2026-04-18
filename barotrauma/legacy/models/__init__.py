"""
Core simulation models for barotrauma risk assessment.

This module contains the primary simulation engines for modeling middle ear
barotrauma risk under various conditions:

- chamber_risk: Hypobaric chamber training risk assessment
- flight_simulation: Flight-based barotrauma models
- physiology: Physiological parameter sets and constants
- risk_analysis: Risk categorization and scoring algorithms
- valsalva_video_analysis: Video-based Valsalva maneuver analysis
- ml_risk_model: Machine learning risk prediction models
- valsalva_chamber_integration: Integration of video analysis with chamber models
"""

from .chamber_risk import HypobaricChamberRiskModel, ChamberScenario

# Valsalva video analysis components
from .valsalva_video_analysis import (
    TMMovementFeatures,
    BilateralValsalvaResult,
    ValsalvaQualityGrade,
    TMMovementExtractor,
    ValsalvaRiskPredictor,
    PatientValsalvaProfile,
    map_valsalva_to_et_dysfunction,
    create_chamber_scenario_from_valsalva,
    generate_clinical_report,
)

# ML models
from .ml_risk_model import (
    TrainingExample,
    LogisticRegressionModel,
    GradientBoostingModel,
    HybridPhysicsMLModel,
    create_model,
)

# Integration
from .valsalva_chamber_integration import (
    IntegratedBarotraumaAssessment,
    IntegratedRiskAssessment,
    quick_assess,
)

__all__ = [
    # Chamber risk model
    "HypobaricChamberRiskModel",
    "ChamberScenario",
    # Valsalva analysis
    "TMMovementFeatures",
    "BilateralValsalvaResult",
    "ValsalvaQualityGrade",
    "TMMovementExtractor",
    "ValsalvaRiskPredictor",
    "PatientValsalvaProfile",
    "map_valsalva_to_et_dysfunction",
    "create_chamber_scenario_from_valsalva",
    "generate_clinical_report",
    # ML models
    "TrainingExample",
    "LogisticRegressionModel",
    "GradientBoostingModel", 
    "HybridPhysicsMLModel",
    "create_model",
    # Integration
    "IntegratedBarotraumaAssessment",
    "IntegratedRiskAssessment",
    "quick_assess",
]
