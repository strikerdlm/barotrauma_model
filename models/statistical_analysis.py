"""
Statistical Analysis Module
Converted from MATLAB implementation by Simon Lansbergen

This module provides statistical analysis tools for the middle ear model,
including confidence interval calculations and other statistical measures.

Original MATLAB implementation (c) Simon Lansbergen, 2016
"""

import numpy as np
from scipy import stats
from typing import Tuple

def calculate_confidence_interval(sample: np.ndarray, df: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate 95% confidence interval bounds
    
    Args:
        sample: Sample data array
        df: Degrees of freedom
        
    Returns:
        Tuple of (upper confidence limit, lower confidence limit)
    """
    SEM = np.std(sample, axis=0) / np.sqrt(df-1)  # Standard Error
    t_score = stats.t.ppf([0.025, 0.975], df-1)   # T-Score, 95% Confidence
    
    mean_sample = np.mean(sample, axis=0)
    CI95_upper = mean_sample + t_score[1] * SEM  # Upper confidence interval
    CI95_lower = mean_sample + t_score[0] * SEM  # Lower confidence interval
    
    return CI95_upper, CI95_lower

def analyze_age_variations(samples: dict) -> Tuple[np.ndarray, np.ndarray]:
    """
    Analyze variations across age groups
    
    Args:
        samples: Dictionary containing samples for different age groups
        
    Returns:
        Tuple of (confidence intervals, mean values)
    """
    combined_samples = np.stack(list(samples.values()))
    df = len(samples)
    
    CI95_upper, CI95_lower = calculate_confidence_interval(combined_samples, df)
    mean_values = np.mean(combined_samples, axis=0)
    
    return (CI95_upper, CI95_lower), mean_values 