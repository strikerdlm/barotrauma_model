"""
Core simulation models for barotrauma risk assessment.

This module contains the primary simulation engines for modeling middle ear
barotrauma risk under various conditions:

- chamber_risk: Hypobaric chamber training risk assessment
- flight_simulation: Flight-based barotrauma models
- physiology: Physiological parameter sets and constants
- risk_analysis: Risk categorization and scoring algorithms
"""

from .chamber_risk import HypobaricChamberRiskModel, ChamberScenario

__all__ = ["HypobaricChamberRiskModel", "ChamberScenario"]
