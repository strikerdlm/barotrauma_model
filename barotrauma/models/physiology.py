"""
Physiological parameters and constants for barotrauma modeling.

This module contains standardized physiological parameters used across
different barotrauma models, based on clinical literature and experimental data.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class PhysiologicalConstants:
    """Standard physiological constants for middle ear modeling."""
    
    # Pressure thresholds (mmHg)
    ET_PASSIVE_OPENING: float = 15.0        # Passive ET opening threshold
    ET_LOCK_THRESHOLD: float = 90.0         # ET lock threshold  
    MEMBRANE_RUPTURE: float = 150.0         # Tympanic membrane rupture threshold
    
    # Anatomical parameters
    ET_LENGTH_MM: float = 35.0              # Eustachian tube length
    ET_DIAMETER_MM: float = 3.0             # Eustachian tube diameter
    TYMPANUM_VOLUME_ML: float = 1.0         # Tympanic cavity volume
    MASTOID_VOLUME_ML: float = 7.75         # Mastoid air cell volume
    
    # Compliance parameters  
    TM_MAX_DISPLACEMENT_ML: float = 0.30    # Maximum TM displacement
    TM_COMPLIANCE: float = 0.003            # TM compliance (mL/mmHg)


@dataclass  
class ETDysfunctionParameters:
    """Parameters for different ET dysfunction severity levels."""
    
    MILD: float = 0.35          # Mild dysfunction coefficient
    MODERATE: float = 0.60      # Moderate dysfunction coefficient  
    SEVERE: float = 0.85        # Severe dysfunction coefficient


# Standard parameter sets for different populations
ADULT_PARAMETERS = PhysiologicalConstants()

PEDIATRIC_PARAMETERS = PhysiologicalConstants(
    ET_LENGTH_MM=25.0,
    ET_DIAMETER_MM=2.0,
    TYMPANUM_VOLUME_ML=0.7,
    MASTOID_VOLUME_ML=4.5,
)
