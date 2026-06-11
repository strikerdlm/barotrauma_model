"""
Statistical Analysis Module
Based on Kanick & Doyle (2005) - J Appl Physiol 98: 1592-1602

This module provides statistical analysis tools for barotrauma simulation results,
including confidence intervals and risk assessments.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class RiskAssessment:
    """Container for risk assessment results"""
    barotitis_probability: float
    baromyringitis_probability: float
    confidence_interval: Tuple[float, float]
    risk_category: str

class StatisticalAnalyzer:
    """Statistical analysis tools for barotrauma simulations"""
    
    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize analyzer
        
        Args:
            confidence_level: Confidence level for intervals (default 0.95)
        """
        self.confidence_level = confidence_level
        
        # Legacy risk categories retained for exploratory summaries.
        self.risk_categories = {
            'low': (0.0, 0.05),
            'moderate': (0.05, 0.25),
            'high': (0.25, 1.0)
        }
        
    def calculate_confidence_interval(self, 
                                   pressure_data: np.ndarray,
                                   df: int) -> Tuple[float, float]:
        """
        Calculate confidence interval for pressure measurements
        
        Args:
            pressure_data: Array of pressure measurements
            df: Degrees of freedom
            
        Returns:
            Tuple of (lower bound, upper bound)
        """
        sem = np.std(pressure_data) / np.sqrt(df)
        t_value = stats.t.ppf((1 + self.confidence_level) / 2, df-1)
        
        mean_value = np.mean(pressure_data)
        ci_lower = mean_value - t_value * sem
        ci_upper = mean_value + t_value * sem
        
        return ci_lower, ci_upper
    
    def assess_risk(self, simulation_results: Dict[str, np.ndarray]) -> RiskAssessment:
        """
        Assess barotrauma risk from simulation results
        
        Args:
            simulation_results: Dictionary of simulation results
            
        Returns:
            RiskAssessment object
        """
        # Calculate probabilities
        barotitis_prob = np.mean(simulation_results['barotitis'])
        baromyringitis_prob = np.mean(simulation_results['baromyringitis'])
        
        # Calculate confidence interval for pressure differential
        ci = self.calculate_confidence_interval(
            simulation_results['dP'],
            len(simulation_results['dP']) - 1
        )
        
        # Determine risk category
        max_prob = max(barotitis_prob, baromyringitis_prob)
        risk_category = 'low'
        for category, (lower, upper) in self.risk_categories.items():
            if lower <= max_prob < upper:
                risk_category = category
                break
                
        return RiskAssessment(
            barotitis_probability=barotitis_prob,
            baromyringitis_probability=baromyringitis_prob,
            confidence_interval=ci,
            risk_category=risk_category
        )
    
    def analyze_age_effects(self, 
                          age_results: Dict[str, Dict[str, np.ndarray]]) -> Dict[str, RiskAssessment]:
        """
        Analyze age-related variations in barotrauma risk
        
        Args:
            age_results: Dictionary of simulation results for different ages
            
        Returns:
            Dictionary of risk assessments by age
        """
        return {
            age: self.assess_risk(results)
            for age, results in age_results.items()
        }
