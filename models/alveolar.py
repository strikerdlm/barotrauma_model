"""
Alveolar Gas Exchange Model
Based on Kanick & Doyle (2005) - J Appl Physiol 98: 1592-1602

This module implements the pulmonary gas exchange components affecting
nasopharyngeal gas composition during flight.
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class AlveolarParameters:
    """Parameters for alveolar gas exchange"""
    
    # Gas partial pressures (mmHg)
    P_O2_alv: float = 100    # Alveolar O2
    P_CO2_alv: float = 40    # Alveolar CO2
    P_H2O_alv: float = 47    # Alveolar H2O (saturated)
    P_N2_alv: float = 573    # Alveolar N2 (balance)
    
    # Exchange coefficients
    D_O2: float = 0.3    # O2 diffusion coefficient
    D_CO2: float = 0.9   # CO2 diffusion coefficient
    D_N2: float = 0.03   # N2 diffusion coefficient

class AlveolarExchange:
    """Implementation of alveolar-blood gas exchange"""
    
    def __init__(self, params: AlveolarParameters):
        """Initialize alveolar exchange model"""
        self.params = params
        
    def calculate_np_partial_pressures(self, 
                                     P_cabin: float, 
                                     breathing_rate: float) -> Dict[str, float]:
        """
        Calculate nasopharyngeal gas partial pressures
        
        Args:
            P_cabin: Cabin pressure (mmHg)
            breathing_rate: Breaths per minute
            
        Returns:
            Dictionary of gas partial pressures in nasopharynx
        """
        # Implement equations 5-7 from paper
        # NP pressure equals cabin pressure
        P_NP = P_cabin
        
        # Calculate partial pressures based on breathing cycle
        P_O2_NP = (self.params.P_O2_alv + P_NP * 0.21) / 2
        P_CO2_NP = (self.params.P_CO2_alv + P_NP * 0.0004) / 2
        P_H2O_NP = self.params.P_H2O_alv  # Assumed saturated
        P_N2_NP = P_NP - P_O2_NP - P_CO2_NP - P_H2O_NP
        
        return {
            'O2': P_O2_NP,
            'CO2': P_CO2_NP,
            'H2O': P_H2O_NP,
            'N2': P_N2_NP
        }
        
    def calculate_blood_partial_pressures(self, 
                                        np_pressures: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate venous blood gas partial pressures
        
        Args:
            np_pressures: Dictionary of NP partial pressures
            
        Returns:
            Dictionary of blood partial pressures
        """
        # Blood O2 and CO2 are buffered
        P_O2_blood = self.params.P_O2_alv * 0.45  # Venous O2
        P_CO2_blood = self.params.P_CO2_alv * 1.15  # Venous CO2
        P_H2O_blood = self.params.P_H2O_alv  # Constant
        
        # N2 follows NP pressure
        P_N2_blood = np_pressures['N2']
        
        return {
            'O2': P_O2_blood,
            'CO2': P_CO2_blood,
            'H2O': P_H2O_blood,
            'N2': P_N2_blood
        } 