"""
Example Usage Script
Based on Kanick & Doyle (2005) - J Appl Physiol 98: 1592-1602

This script demonstrates how to use the middle ear barotrauma model
for various simulation scenarios.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

from .integrated_model import IntegratedModel, SimulationConfig
from analysis.statistical_analysis import StatisticalAnalyzer

def run_age_comparison():
    """Compare barotrauma risk across different ages"""
    # Define age groups to simulate
    age_groups = {
        'infant': 1,      # 1 month
        'toddler': 12,    # 12 months
        'child': 60,      # 5 years
        'adult': 240      # 20 years
    }
    
    # Setup flight profile (PIT to MIA)
    base_config = SimulationConfig(
        departure_airport='PIT',
        destination_airport='MIA'
    )
    
    # Run simulations for each age group
    results = {}
    for age_label, age_months in age_groups.items():
        config = base_config
        config.age_months = age_months
        
        model = IntegratedModel(config)
        results[age_label] = model.run_simulation()
        
    # Analyze results
    analyzer = StatisticalAnalyzer()
    risk_assessments = analyzer.analyze_age_effects(results)
    
    # Plot results
    plot_age_comparison(results, risk_assessments)
    
def run_pathology_comparison():
    """Compare different pathological conditions"""
    # Define conditions to simulate
    conditions = {
        'normal': None,
        'et_obstruction': 'et_obstruction',
        'poor_mtvp': 'poor_mtvp',
        'hypercompliant_tm': 'hypercompliant_tm'
    }
    
    # Setup base configuration
    base_config = SimulationConfig(
        departure_airport='PIT',
        destination_airport='DEN'
    )
    
    # Run simulations for each condition
    results = {}
    for label, pathology in conditions.items():
        config = base_config
        config.pathology = pathology
        if pathology == 'poor_mtvp':
            config.pathology_severity = 0.7
            
        model = IntegratedModel(config)
        results[label] = model.run_simulation()
        
    # Analyze and plot results
    analyzer = StatisticalAnalyzer()
    risk_assessments = {
        label: analyzer.assess_risk(result)
        for label, result in results.items()
    }
    
    plot_pathology_comparison(results, risk_assessments)

def plot_age_comparison(results: Dict[str, Dict[str, np.ndarray]], 
                       risk_assessments: Dict[str, RiskAssessment]):
    """Plot comparison of age-related effects"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    # Plot pressure differentials
    for age, result in results.items():
        ax1.plot(result['time'], result['dP'], label=age)
    
    ax1.axhline(y=250, color='r', linestyle='--', label='Barotitis Threshold')
    ax1.axhline(y=1300, color='r', linestyle=':', label='Baromyringitis Threshold')
    ax1.set_xlabel('Time (min)')
    ax1.set_ylabel('ΔP_ME-cabin (mmH2O)')
    ax1.legend()
    ax1.grid(True)
    
    # Plot risk assessment
    ages = list(results.keys())
    barotitis_risks = [risk_assessments[age].barotitis_probability for age in ages]
    baromyringitis_risks = [risk_assessments[age].baromyringitis_probability for age in ages]
    
    x = np.arange(len(ages))
    width = 0.35
    
    ax2.bar(x - width/2, barotitis_risks, width, label='Barotitis Risk')
    ax2.bar(x + width/2, baromyringitis_risks, width, label='Baromyringitis Risk')
    
    ax2.set_xlabel('Age Group')
    ax2.set_ylabel('Risk Probability')
    ax2.set_xticks(x)
    ax2.set_xticklabels(ages)
    ax2.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_age_comparison()
    run_pathology_comparison() 