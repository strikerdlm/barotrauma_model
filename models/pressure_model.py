"""
Pressure Model Implementation
Converted from MATLAB implementation by Simon Lansbergen

This module implements the pressure calculations for the middle ear model.
The function adds pressure variation according to the Vanhuyse theoretical framework.

Original MATLAB implementation (c) Simon Lansbergen, 2016
"""

import numpy as np
from typing import NamedTuple
from dataclasses import dataclass

class PressureSolution(NamedTuple):
    """Container for pressure calculation results"""
    Rp: np.ndarray   # Resistance with pressure
    Xp: np.ndarray   # Reactance with pressure
    Z: np.ndarray    # Complex impedance
    Y: np.ndarray    # Complex admittance
    Yabs: np.ndarray # Absolute admittance
    G: np.ndarray    # Conductance
    B: np.ndarray    # Susceptance

def calculate_pressure_response(params, R_input: np.ndarray, X_input: np.ndarray) -> PressureSolution:
    """
    Calculate pressure response for given resistance and reactance
    
    Args:
        params: Model parameters
        R_input: Input resistance array
        X_input: Input reactance array
        
    Returns:
        PressureSolution containing pressure-dependent values
    """
    # Create pressure array
    p = np.arange(-300, 301)  # -300 to 300 daPa
    wp = 2.5  # Width reactance parabola

    # Vectorized pressure function for Resistance
    R_matrix = R_input[:, np.newaxis] * np.ones((1, len(p)))
    pressure_effect = 300 * np.exp(-(p-100)/600) - 354.4
    Rp = R_matrix + np.ones((len(R_input), 1)) @ pressure_effect[np.newaxis, :]

    # Vectorized pressure function for Reactance
    X_matrix = X_input[:, np.newaxis] * np.ones((1, len(p)))
    pressure_parabola = -((p/wp)**2)
    Xp = X_matrix + np.ones((len(X_input), 1)) @ pressure_parabola[np.newaxis, :]

    # Calculate derived quantities
    Z = Rp + 1j * Xp
    Y = 1/Z
    Yabs = np.abs(Y)
    G = np.real(Y)
    B = np.imag(Y)

    return PressureSolution(Rp, Xp, Z, Y, Yabs, G, B) 