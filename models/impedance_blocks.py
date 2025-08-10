"""
Impedance Blocks Implementation
Converted from MATLAB implementation by Simon Lansbergen

This module contains the impedance block calculations for the middle ear model:
- Block 1a (Z1a)
- Block 1b (Z1b)
- Block 2 (Z2)
- Block 3 (Z3)
- Block 4 (Z4)
- Block 5 (Z5)

Original MATLAB implementation (c) Simon Lansbergen, 2016
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class ImpedanceParameters:
    """Parameters for impedance calculations"""
    # Block 1a parameters
    La: float = 0.0  # Inertance
    Ca: float = 0.0  # Compliance
    Ra: float = 0.0  # Resistance
    Ct: float = 0.0  # Compliance
    
    # Block 1b parameters
    Ld: float = 7.5e-3  # Inertance
    Ls: float = 66e-3   # Resistance
    Cs: float = 0.3e-6  # Compliance
    Rs: float = 20      # Resistance
    Cr: float = 1.3e-6  # Compliance
    Rr: float = 120     # Resistance
    
    # Block 2 parameters
    Cm: float = 0.38e-6  # Compliance
    Rm: float = 120      # Resistance
    
    # Block 3 parameters
    Lo: float = 22e-3    # Inertance
    Co: float = np.inf   # Compliance
    Ro: float = 20       # Resistance
    
    # Block 4 parameters
    Ci: float = 0.3e-6   # Compliance
    Ri: float = 6000     # Resistance
    
    # Block 5 parameters
    Lc: float = 46e-3    # Inertance
    Cc: float = 0.56e-6  # Compliance
    Rc: float = 330      # Resistance

def calculate_block_1a(params: ImpedanceParameters, w: np.ndarray) -> np.ndarray:
    """
    Calculate impedance for block 1a
    
    Args:
        params: Impedance parameters
        w: Angular frequencies
        
    Returns:
        Complex impedance array
    """
    # Calculate reactances
    Xl1 = w * params.La
    Xc1 = 1 / (w * params.Ca)
    Xeq_1 = Xl1 - Xc1
    
    # Part 1 impedance
    Z1 = params.Ra + 1j * Xeq_1
    
    # Part 2 impedance (Ct only)
    Xc2 = 1 / (w * params.Ct)
    Z2 = 1j * (-Xc2)
    
    # Parallel combination
    Z1a = (Z1 * Z2) / (Z1 + Z2)
    
    return Z1a

def calculate_block_1b(params: ImpedanceParameters, w: np.ndarray) -> np.ndarray:
    """Calculate impedance for block 1b"""
    # First stage
    Xl1 = w * params.Ls
    Xc1 = 1 / (w * params.Cs)
    Z1 = params.Rs + 1j * (Xl1 - Xc1)
    
    # Second stage
    Xc2 = 1 / (w * params.Cr)
    Z2 = params.Rr + 1j * (-Xc2)
    
    # Parallel combination
    Zeq = (Z1 * Z2) / (Z1 + Z2)
    
    # Add final inertance
    Z1b = Zeq + 1j * (w * params.Ld)
    
    return Z1b

def calculate_block_2(params: ImpedanceParameters, w: np.ndarray) -> np.ndarray:
    """Calculate impedance for block 2"""
    Xc = 1 / (w * params.Cm)
    return params.Rm + 1j * (-Xc)

def calculate_block_3(params: ImpedanceParameters, w: np.ndarray) -> np.ndarray:
    """Calculate impedance for block 3"""
    Xl = w * params.Lo
    return params.Ro + 1j * Xl

def calculate_block_4(params: ImpedanceParameters, w: np.ndarray) -> np.ndarray:
    """Calculate impedance for block 4"""
    Xc = 1 / (w * params.Ci)
    return params.Ri + 1j * (-Xc)

def calculate_block_5(params: ImpedanceParameters, w: np.ndarray) -> np.ndarray:
    """Calculate impedance for block 5"""
    Xl = w * params.Lc
    Xc = 1 / (w * params.Cc)
    return params.Rc + 1j * (Xl - Xc) 