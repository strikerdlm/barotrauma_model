"""
Plotting Utilities
Converted from MATLAB implementation by Simon Lansbergen

This module provides plotting functions for visualizing middle ear model results,
including tympanograms, impedance plots, and statistical analysis results.

Original MATLAB implementation (c) Simon Lansbergen, 2016
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PlotSettings:
    """Settings for plot customization"""
    line_width: float = 3.0
    marker_style1: str = '-'  # Solid line
    marker_style2: str = '--'  # Dashed line
    freq_ticks: list = None
    
    def __post_init__(self):
        if self.freq_ticks is None:
            self.freq_ticks = [100, 250, 500, 750, 1000, 1250, 1500]

def plot_tympanogram(pressure_data, frequencies: list, settings: Optional[PlotSettings] = None):
    """
    Plot tympanograms at different frequencies
    
    Args:
        pressure_data: Pressure response data
        frequencies: List of frequencies to plot
        settings: Plot customization settings
    """
    settings = settings or PlotSettings()
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    # Vertical separation for stacked plots
    sep = 0.0075
    
    # Plot conductance (G)
    ax1.set_title('Conductance (G)')
    for i, freq in enumerate(frequencies):
        ax1.plot(np.arange(-300, 301), 
                pressure_data.G[freq] + i*sep,
                settings.marker_style1 if i%2==0 else settings.marker_style2,
                linewidth=settings.line_width)
    ax1.set_xlim(-300, 300)
    ax1.set_ylim(0, 0.05)
    ax1.grid(False)
    
    # Plot susceptance (B)
    ax2.set_title('Susceptance (B)')
    for i, freq in enumerate(frequencies):
        ax2.plot(np.arange(-300, 301), 
                pressure_data.B[freq] + i*sep,
                settings.marker_style1 if i%2==0 else settings.marker_style2,
                linewidth=settings.line_width)
    ax2.set_xlim(-300, 300)
    ax2.set_ylim(0, 0.05)
    ax2.grid(False)
    
    # Plot admittance magnitude (|Y|)
    ax3.set_title('Admittance |Y|')
    for i, freq in enumerate(frequencies):
        ax3.plot(np.arange(-300, 301), 
                pressure_data.Yabs[freq] + i*sep,
                settings.marker_style1 if i%2==0 else settings.marker_style2,
                linewidth=settings.line_width)
    ax3.set_xlim(-300, 300)
    ax3.set_ylim(0, 0.05)
    ax3.grid(False)
    
    plt.tight_layout()
    
def plot_impedance_comparison(freq: np.ndarray, 
                            impedances: Dict[str, Tuple[np.ndarray, np.ndarray]], 
                            settings: Optional[PlotSettings] = None):
    """
    Plot impedance comparisons between different conditions
    
    Args:
        freq: Frequency array
        impedances: Dictionary of (resistance, reactance) tuples for different conditions
        settings: Plot customization settings
    """
    settings = settings or PlotSettings()
    
    plt.figure(figsize=(10, 6))
    
    for label, (R, X) in impedances.items():
        plt.semilogx(freq, R, settings.marker_style1, 
                    freq, X, settings.marker_style2,
                    linewidth=settings.line_width,
                    label=f'{label} R/X')
    
    plt.grid(True)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Impedance (Acoustic Ohm)')
    plt.title('Impedance Comparison')
    plt.legend()
    plt.xticks(settings.freq_ticks)
    
def plot_confidence_intervals(freq: np.ndarray,
                            ci_upper: np.ndarray,
                            ci_lower: np.ndarray,
                            mean_values: np.ndarray,
                            settings: Optional[PlotSettings] = None):
    """
    Plot confidence intervals with mean values
    
    Args:
        freq: Frequency array
        ci_upper: Upper confidence interval
        ci_lower: Lower confidence interval
        mean_values: Mean values
        settings: Plot customization settings
    """
    settings = settings or PlotSettings()
    
    plt.figure(figsize=(10, 6))
    plt.semilogx(freq, ci_upper, 'r', freq, ci_lower, 'r',
                 linewidth=settings.line_width)
    plt.semilogx(freq, mean_values, 'k--', linewidth=settings.line_width)
    
    plt.grid(True)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Impedance (Acoustic Ohm)')
    plt.title('95% Confidence Intervals')
    plt.xticks(settings.freq_ticks)
    plt.axis([100, 1500, -2000, 1000]) 