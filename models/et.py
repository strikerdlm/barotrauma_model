"""
Eustachian Tube Model
Based on Kanick & Doyle (2005) - J Appl Physiol 98: 1592-1602

This module implements the Eustachian tube (ET) mechanics and gas exchange
as described in the barotrauma model.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class ETParameters:
    """Parameters describing ET function"""
    
    # ET opening pressures (mmH2O) from Table 1
    P_ME_ET_O: float = 350  # ME-side opening pressure
    P_NP_ET_O: float = 600  # NP-side opening pressure
    P_C: float = 100        # Closing pressure
    
    # ET dimensions and properties
    length: float = 3.7     # cm
    width: float = 0.1      # cm
    compliance: float = 1.0  # relative units
    
    # Muscle parameters
    mTVP_force: float = 1.0  # Relative force units
    
class EustachianTube:
    """Implementation of ET mechanics and gas exchange"""
    
    def __init__(self, params: ETParameters):
        """Initialize ET model"""
        self.params = params
        
    def calculate_opening_force(self, P_ME: float, P_NP: float, P_ET: float) -> float:
        """
        Calculate force acting to open ET
        
        Args:
            P_ME: Middle ear pressure
            P_NP: Nasopharyngeal pressure
            P_ET: ET tissue pressure
            
        Returns:
            Net opening force
        """
        # Implement equation 8 from paper
        A_ET = np.pi * (self.params.width/2)**2
        F_ST = 0.1  # Surface tension force (arbitrary units)
        return P_ET * A_ET + F_ST
    
    def calculate_gas_flow(self, 
                          P_ME: float, 
                          P_NP: float, 
                          F_mTVP: Optional[float] = None) -> float:
        """
        Calculate gas flow through ET
        
        Args:
            P_ME: Middle ear pressure
            P_NP: Nasopharyngeal pressure
            F_mTVP: Optional muscle force
            
        Returns:
            Gas flow rate (ml/min)
        """
        # Implement equations 14-15 from paper
        if F_mTVP is not None:
            # Active opening
            X_ET = F_mTVP * self.params.compliance
            dP = P_ME - P_NP
            Q = (2/3) * (dP * X_ET**3 * self.params.width) / (0.018 * self.params.length)
            return Q
        else:
            # Passive opening
            return 0.0
            
    def is_locked(self, P_ME: float, P_NP: float) -> bool:
        """
        Determine if ET is "locked" due to large pressure differential
        
        Args:
            P_ME: Middle ear pressure
            P_NP: Nasopharyngeal pressure
            
        Returns:
            Boolean indicating if ET is locked
        """
        # Implement ET locking criterion
        dP = abs(P_ME - P_NP)
        return dP > 2000  # mmH2O threshold for locking 