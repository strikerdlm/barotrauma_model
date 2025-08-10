"""
Keefe Ear Canal Model Implementation
Converted from MATLAB implementation by Simon Lansbergen

This module implements the Keefe ear canal model based on:
- Vocal tract modeling by Guelke and Bunn (1981)
- Keefe's ear canal model adaptations

Original MATLAB implementation (c) Simon Lansbergen, 2016
"""

import numpy as np
from typing import NamedTuple
from dataclasses import dataclass

class KeefeSolution(NamedTuple):
    """Container for Keefe model solutions"""
    Zk: np.ndarray  # Total impedance
    Rk: np.ndarray  # Resistance
    Xk: np.ndarray  # Reactance
    Gk: np.ndarray  # Conductance
    Bk: np.ndarray  # Susceptance
    Yk: np.ndarray  # Admittance

def calculate_keefe_model(params, kr, w: np.ndarray) -> KeefeSolution:
    """
    Calculate the Keefe ear canal model solution
    
    Args:
        params: Model parameters
        kr: Kringlebotn model results
        w: Angular frequencies
        
    Returns:
        KeefeSolution containing all computed values
    """
    # Calculate inertance and compliance
    Lv = params.rho * params.Vec
    Cv = 1 / (w * ((params.rho * params.c) / (np.pi * (params.d/2)**2)) * (2/(w/params.c) * params.l))
    
    # Middle ear components
    Lm = kr.Xeq / w
    Cm = -1 / (w * kr.Xeq)
    
    # Wall admittance calculations
    Bm = -kr.Xeq / (kr.Req**2 + kr.Xeq**2)
    Cm_s = Bm / w
    Cw = params.fCC * Cm_s
    
    step1 = Cw * w * (1 - (w/params.Ww)**2) * 1j + (params.Ww * Cw) / params.Qw
    step2 = ((1 - (w/params.Ww)**2)**2) + (w/(params.Ww * params.Qw))**2
    
    # Calculate impedances
    Xcv = np.abs(-1/(w * Cv))
    Xlv = Lv * w
    Xv = Xlv - Xcv
    Zv = 1j * Xv
    
    # Combined impedances
    totC = Cm + Cv
    totX = -1/(w * totC)
    totR = kr.Req
    
    # Wall effect
    Yw = step1 / step2
    Gw = np.real(Yw)
    Bw = np.imag(Yw)
    Zw = (Gw - 1j * Bw) / (Gw**2 + Bw**2)
    
    # Total impedance calculation
    Z = totR + 1j * totX
    
    if params.onoff == 0:  # With compliant wall effect
        Zk = Z * Zw / (Z + Zw)
        Xk = np.imag(Zk) + params.addC
        Rk = np.real(Zk) if not params.fixR_onoff else np.full_like(w, params.fixR)
    else:  # Neglect compliant wall effect
        Zk = Z
        Xk = np.imag(Zk) + params.addC
        Rk = np.real(Zk) if not params.fixR_onoff else np.full_like(w, params.fixR)
    
    # Calculate admittance components
    Gk = Rk / (Xk**2 + Rk**2)
    Bk = -Xk / (Xk**2 + Rk**2)
    Yk = Gk + 1j * Bk
    
    return KeefeSolution(Zk, Rk, Xk, Gk, Bk, Yk) 