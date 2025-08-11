"""
Barotrauma Model: Physiological Risk Assessment for Aviation Medicine

A comprehensive Python package for modeling middle ear barotrauma risk during
altitude changes, with applications in aviation medicine, hypobaric chamber
training, and clinical research.

Main modules:
- models: Core simulation and risk assessment models
- analysis: Statistical analysis and visualization tools  
- utils: Shared utilities and helper functions
"""

from .models import chamber_risk
from .models.chamber_risk import HypobaricChamberRiskModel, ChamberScenario

__version__ = "1.0.0"
__author__ = "Dr. Daniel Malpica"
__email__ = "dlmalpica@me.com"

__all__ = [
    "HypobaricChamberRiskModel",
    "ChamberScenario",
    "chamber_risk",
]
