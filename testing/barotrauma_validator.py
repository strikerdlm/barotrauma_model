"""
Comprehensive validation framework for the integrated barotrauma model.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (roc_auc_score, precision_recall_curve, 
                           average_precision_score, brier_score_loss)
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

from .barotrauma_integrated_model import IntegratedBarotraumaModel
from .barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile
from .physiological_validator import PhysiologicalValidator

class BarotraumaValidator:
    """Comprehensive validation suite for integrated barotrauma model."""
    
    def __init__(self, model: IntegratedBarotraumaModel):
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.validation_results = {}
        
        # Physiological bounds for validation
        self.phys_bounds = {
            'pressure_diff_max': 200,  # mmHg
            'volume_change_max': 3.0,  # mL
            'et_dysfunction_range': (0, 1),
            'gas_exchange_max': 1e-4,  # mol/s
            'compliance_max': 1e-4  # L/mmHg
        }
        
        self.phys_validator = PhysiologicalValidator()
    
    def generate_validation_scenarios(self, n_samples: int = 1000) -> List[Dict]:
        """Generate diverse validation scenarios."""
        scenarios = []
        
        # Generate scenarios with physiologically plausible distributions
        for _ in range(n_samples):
            et_dysfunction = np.random.beta(2, 2)  # Beta distribution for ET dysfunction
            
            scenario = {
                'initial_altitude_ft': 0,
                'final_altitude_ft': np.random.uniform(20000, 40000),
                'climb_rate_ft_min': np.random.uniform(1000, 3000),
                'descent_rate_ft_min': np.random.uniform(1000, 3000),
                'cruise_duration_min': np.random.uniform(10, 60),
                'et_dysfunction': et_dysfunction,
                'V_tym': np.random.normal(1.0e-3, 0.2e-3),
                'V_mas': np.random.normal(7.75e-3, 0.5e-3),
                'mastoid_compliance': np.random.lognormal(-11.5, 0.5),
                'k_MEM': {
                    'O2': np.random.lognormal(-4.2, 0.3),
                    'CO2': np.random.lognormal(-3.7, 0.3),
                    'N2': np.random.lognormal(-7, 0.3),
                    'H2O': np.random.lognormal(-3.4, 0.3)
                }
            }
            scenarios.append(scenario)
        
        return scenarios
    
    def validate_physiological_bounds(self, scenarios: List[Dict]) -> Dict:
        """Validate that predictions respect physiological bounds."""
        predictions, uncertainties = self.model.predict(scenarios, return_uncertainty=True)
        
        # Check bounds
        bound_violations = {
            'pressure_differential': [],
            'volume_change': [],
            'et_function': [],
            'uncertainty': []
        }
        
        for i, scenario in enumerate(scenarios):
            features = self.model._extract_physical_features(scenario)
            
            if features.pressure_differential > self.phys_bounds['pressure_diff_max']:
                bound_violations['pressure_differential'].append(i)
            
            if features.volume_change > self.phys_bounds['volume_change_max']:
                bound_violations['volume_change'].append(i)
            
            if not (self.phys_bounds['et_dysfunction_range'][0] <= features.et_function <= 
                   self.phys_bounds['et_dysfunction_range'][1]):
                bound_violations['et_function'].append(i)
            
            if uncertainties[i] > 0.5:  # High uncertainty threshold
                bound_violations['uncertainty'].append(i)
        
        return bound_violations
    
    def validate_model_performance(self, X_val: np.ndarray, y_val: np.ndarray) -> Dict:
        """Validate model performance with multiple metrics."""
        # Get predictions
        predictions, uncertainties = self.model.predict(X_val, return_uncertainty=True)
        
        # Calculate metrics
        metrics = {
            'roc_auc': roc_auc_score(y_val, predictions),
            'avg_precision': average_precision_score(y_val, predictions),
            'brier_score': brier_score_loss(y_val, predictions),
            'mean_uncertainty': np.mean(uncertainties),
            'uncertainty_correlation': np.corrcoef(uncertainties, 
                                                 np.abs(predictions - y_val))[0,1]
        }
        
        return metrics
    
    def validate_calibration(self, X_val: np.ndarray, y_val: np.ndarray, 
                           n_bins: int = 10) -> Dict:
        """Validate model calibration."""
        predictions, _ = self.model.predict(X_val)
        
        # Calculate calibration metrics
        bin_edges = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(predictions, bin_edges) - 1
        
        calibration_data = {
            'bin_edges': bin_edges,
            'pred_probs': [],
            'true_probs': [],
            'counts': []
        }
        
        for i in range(n_bins):
            mask = bin_indices == i
            if np.sum(mask) > 0:
                calibration_data['pred_probs'].append(np.mean(predictions[mask]))
                calibration_data['true_probs'].append(np.mean(y_val[mask]))
                calibration_data['counts'].append(np.sum(mask))
        
        return calibration_data
    
    def plot_validation_results(self, save_dir: Optional[Path] = None):
        """Generate comprehensive validation plots."""
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Plot 1: Calibration curve
        plt.figure(figsize=(10, 10))
        cal_data = self.validation_results.get('calibration', {})
        if cal_data:
            plt.plot(cal_data['pred_probs'], cal_data['true_probs'], 'bo-', 
                    label='Calibration curve')
            plt.plot([0, 1], [0, 1], 'r--', label='Perfect calibration')
            plt.xlabel('Predicted probability')
            plt.ylabel('True probability')
            plt.title('Model Calibration')
            plt.legend()
            
            if save_dir:
                plt.savefig(save_dir / 'calibration.pdf')
            plt.close()
        
        # Plot 2: Uncertainty distribution
        if 'uncertainties' in self.validation_results:
            plt.figure(figsize=(10, 6))
            sns.histplot(self.validation_results['uncertainties'], bins=50)
            plt.xlabel('Prediction uncertainty')
            plt.ylabel('Count')
            plt.title('Uncertainty Distribution')
            
            if save_dir:
                plt.savefig(save_dir / 'uncertainty_dist.pdf')
            plt.close()
    
    def generate_validation_report(self, save_path: Optional[Path] = None) -> str:
        """Generate detailed validation report."""
        report = ["Barotrauma Model Validation Report", "=" * 40, ""]
        
        # Add performance metrics
        if 'metrics' in self.validation_results:
            report.extend([
                "Performance Metrics:",
                "-" * 20,
                f"ROC AUC: {self.validation_results['metrics']['roc_auc']:.3f}",
                f"Average Precision: {self.validation_results['metrics']['avg_precision']:.3f}",
                f"Brier Score: {self.validation_results['metrics']['brier_score']:.3f}",
                f"Mean Uncertainty: {self.validation_results['metrics']['mean_uncertainty']:.3f}",
                ""
            ])
        
        # Add physiological bound violations
        if 'bound_violations' in self.validation_results:
            violations = self.validation_results['bound_violations']
            report.extend([
                "Physiological Bound Violations:",
                "-" * 30,
                f"Pressure Differential: {len(violations['pressure_differential'])} violations",
                f"Volume Change: {len(violations['volume_change'])} violations",
                f"ET Function: {len(violations['et_function'])} violations",
                f"High Uncertainty: {len(violations['uncertainty'])} cases",
                ""
            ])
        
        report_text = "\n".join(report)
        if save_path:
            save_path.write_text(report_text)
        
        return report_text 
    
    def validate_model(self, scenarios: List[Dict]) -> Dict:
        """Comprehensive model validation including physiological aspects."""
        validation_results = {}
        
        # Run standard validation
        validation_results['bounds'] = self.validate_physiological_bounds(scenarios)
        
        # Run physiological validation
        phys_validation = {}
        for scenario in scenarios:
            # Run simulation
            sim_results = self.model._simulate_scenario(scenario)
            
            if sim_results:
                # Validate pressure dynamics
                phys_validation['pressure'] = self.phys_validator.validate_pressure_dynamics(
                    sim_results['pressure_history'],
                    sim_results['time']
                )
                
                # Validate volume changes
                phys_validation['volume'] = self.phys_validator.validate_volume_changes(
                    sim_results['volume_history'],
                    sim_results['time']
                )
                
                # Validate gas exchange
                phys_validation['gas_exchange'] = self.phys_validator.validate_gas_exchange(
                    sim_results['gas_exchange_rates']
                )
        
        validation_results['physiological'] = phys_validation
        
        # Generate plots
        self.phys_validator.plot_physiological_validation(
            sim_results,
            save_dir=Path("results/physiological_validation")
        )
        
        return validation_results