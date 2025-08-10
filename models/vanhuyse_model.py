"""
Vanhuyse Ear Canal Model Implementation
Converted from MATLAB implementation by Simon Lansbergen

This module implements the Vanhuyse ear canal model based on:
Vanhuyse et al. (1975)

Original MATLAB implementation (c) Simon Lansbergen, 2016
"""

import numpy as np
from typing import NamedTuple
from dataclasses import dataclass

class VanhuyseSolution(NamedTuple):
    """Container for Vanhuyse model solutions"""
    Zv: np.ndarray  # Total impedance
    Rv: np.ndarray  # Resistance
    Xv: np.ndarray  # Reactance
    Yv: np.ndarray  # Admittance
    Bv: np.ndarray  # Susceptance
    Gv: np.ndarray  # Conductance
    x: np.ndarray   # Additional parameter

def calculate_vanhuyse_model(params, kr, w: np.ndarray) -> VanhuyseSolution:
    """
    Calculate the Vanhuyse ear canal model solution
    
    Args:
        params: Model parameters
        kr: Kringlebotn model results
        w: Angular frequencies
        
    Returns:
        VanhuyseSolution containing all computed values
    """
    # Calculate local variables
    S = np.pi * (params.d/2)**2  # Cross sectional area ear-canal cm^2
    k = w / params.c
    a = params.rho * params.c / S  # Characteristic impedance ear-canal
    b = np.tan(k * params.l)
    ab = a * b
    x = kr.Xeq + ab

    # Calculate relations
    Gv = ((1 + b**2) * kr.Req) / (x**2 + kr.Req**2)
    Bv = (b/a) - (((1 + b**2) * x) / (x**2 + kr.Req**2))
    Yv = Gv + 1j * Bv

    # Calculate impedance components
    Zv = a * ((kr.Req + (kr.Xeq + a*b)*1j) / (a - b*kr.Xeq + (b*kr.Req)*1j))
    Rv = np.real(Zv)
    Xv = np.imag(Zv)

    return VanhuyseSolution(Zv, Rv, Xv, Yv, Bv, Gv, x) 