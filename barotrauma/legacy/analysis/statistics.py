"""
Statistical Analysis Module
Based on Kanick & Doyle (2005) - J Appl Physiol 98: 1592-1602

This module provides statistical analysis tools for barotrauma simulation results,
including confidence intervals and risk assessments.
"""

import numpy as np
# Make SciPy optional for environments without heavy deps
try:
	from scipy import stats as scipy_stats  # type: ignore
except Exception:  # pragma: no cover - optional dependency
	scipy_stats = None  # Fallback handled in calculate_confidence_interval
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
# Make pandas optional (only required for metrics_dataframe)
try:
	import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional dependency
	pd = None  # type: ignore

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
        
        # Risk categories based on paper
        self.risk_categories = {
            'low': (0.0, 0.05),
            'moderate': (0.05, 0.25),
            'high': (0.25, 1.0)
        }
        
    def compute_metrics(self, simulation_results: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Compute key validation metrics from simulation results."""
        dP = simulation_results['dP']
        eq = simulation_results.get('equalization_rate', np.zeros_like(dP))
        metrics = {
            'max_abs_deltaP_mmHg': float(np.max(np.abs(dP))),
            'mean_abs_deltaP_mmHg': float(np.mean(np.abs(dP))),
            'time_above_lock_frac': float(np.mean(np.abs(dP) > 90.0)),
            'time_above_rupture_frac': float(np.mean(np.abs(dP) > 150.0)),
            'mean_equalization_rate': float(np.mean(eq)),
        }
        return metrics
    
    def metrics_dataframe(self, scenarios: List[Dict],
                          results_list: List[Dict[str, np.ndarray]]) -> 'pd.DataFrame':
        """Assemble a tidy DataFrame of metrics across scenarios.
        Requires pandas; raises if unavailable.
        """
        if pd is None:
            raise ImportError("pandas is required for metrics_dataframe but is not installed")
        rows = []
        for scenario, results in zip(scenarios, results_list):
            m = self.compute_metrics(results)
            row = {
                'et_severity': scenario.get('et_severity', 'n/a'),
                'descent_rate_ft_min': scenario.get('descent_rate_ft_min', np.nan),
                **m,
            }
            rows.append(row)
        return pd.DataFrame(rows)  # type: ignore
        
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
        sem = float(np.std(pressure_data)) / float(np.sqrt(max(df, 1)))
        # Prefer Student's t from SciPy if available; otherwise normal approx
        if scipy_stats is not None:
            t_value = float(scipy_stats.t.ppf((1 + self.confidence_level) / 2, max(df - 1, 1)))
        else:
            # Normal approximation for common confidence levels
            level_rounded = round(self.confidence_level, 2)
            z_map = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
            t_value = float(z_map.get(level_rounded, 1.96))
        
        mean_value = float(np.mean(pressure_data))
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
        barotitis_prob = float(np.mean(simulation_results['barotitis']))
        baromyringitis_prob = float(np.mean(simulation_results['baromyringitis']))
        
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