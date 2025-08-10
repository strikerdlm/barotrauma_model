"""
Physiology Model for Middle Ear Barotrauma
Based on Kanick & Doyle (2005) - J Appl Physiol 98: 1592-1602

This module implements the physiological parameters and relationships
described in the barotrauma model, including age-related variations
and pathological conditions.
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

@dataclass
class PhysiologyParameters:
    """Physiological parameters affecting middle ear pressure regulation"""
    
    # Gas exchange constants (min^-1) from Table 2
    k_O2: float = 0.008    # Oxygen exchange rate
    k_CO2: float = 0.16    # Carbon dioxide exchange rate 
    k_N2: float = 0.0008   # Nitrogen exchange rate
    k_H2O: float = 0.32    # Water vapor exchange rate
    
    # Initial partial pressures (mmHg) from Table 2
    P_ME_O2: float = 40    # ME oxygen pressure
    P_ME_CO2: float = 46   # ME carbon dioxide pressure
    P_ME_H2O: float = 47   # ME water vapor pressure
    P_ME_N2: float = 627   # ME nitrogen pressure (balance)
    
    # Blood pressures (mmHg) from Table 2
    P_VB_O2: float = 45    # Venous blood oxygen pressure
    P_VB_CO2: float = 46   # Venous blood CO2 pressure
    P_VB_H2O: float = 47   # Venous blood water vapor pressure
    P_VB_N2: float = 573   # Venous blood N2 pressure (balance)

    def calculate_total_pressure(self, partial_pressures: Dict[str, float]) -> float:
        """Calculate total pressure from partial pressures"""
        return sum(partial_pressures.values())

class AgeRelatedParameters:
    """Age-dependent physiological parameters"""
    
    def __init__(self, age_months: int):
        """
        Initialize age-specific parameters
        
        Args:
            age_months: Age in months
        """
        self.age_months = age_months
        self.parameters = self._get_age_parameters()
        
    def _get_age_parameters(self) -> Dict[str, float]:
        """Get age-specific physiological parameters"""
        if self.age_months <= 1:  # 1 month old
            return {
                'ear_canal_length': 0.9,    # cm
                'ear_canal_diameter': 0.44,  # cm
                'me_cavity_volume': 2.0,     # cc
                'et_resistance': 160.0,      # mmHg/ml/min
                'tm_compliance': 2.5         # relative units
            }
        elif self.age_months <= 3:  # 3 months old
            return {
                'ear_canal_length': 1.15,
                'ear_canal_diameter': 0.54,
                'me_cavity_volume': 4.0,
                'et_resistance': 140.0,
                'tm_compliance': 2.0
            }
        elif self.age_months <= 6:  # 6 months old
            return {
                'ear_canal_length': 1.25,
                'ear_canal_diameter': 0.63,
                'me_cavity_volume': 6.0,
                'et_resistance': 120.0,
                'tm_compliance': 1.5
            }
        else:  # Adult
            return {
                'ear_canal_length': 2.5,
                'ear_canal_diameter': 1.4,
                'me_cavity_volume': 12.0,
                'et_resistance': 60.0,
                'tm_compliance': 1.0
            }

class PathologicalConditions:
    """Implementation of pathological conditions affecting ME pressure regulation"""
    
    @staticmethod
    def et_obstruction(params: PhysiologyParameters) -> PhysiologyParameters:
        """Simulate complete ET obstruction"""
        modified_params = params
        modified_params.k_O2 = 0  # Block gas exchange
        modified_params.k_CO2 = 0
        modified_params.k_N2 = 0
        return modified_params
    
    @staticmethod
    def poor_mtvp_function(params: PhysiologyParameters, severity: float = 0.5) -> PhysiologyParameters:
        """
        Simulate poor tensor veli palatini muscle function
        
        Args:
            severity: Factor between 0-1 indicating severity (1 = complete dysfunction)
        """
        modified_params = params
        # Reduce gas exchange rates proportionally to severity
        modified_params.k_O2 *= (1 - severity)
        modified_params.k_CO2 *= (1 - severity)
        modified_params.k_N2 *= (1 - severity)
        return modified_params
    
    @staticmethod
    def hypercompliant_tm(params: PhysiologyParameters, factor: float = 2.0) -> PhysiologyParameters:
        """Simulate hypercompliant tympanic membrane"""
        modified_params = params
        # Increase compliance-related parameters
        return modified_params 