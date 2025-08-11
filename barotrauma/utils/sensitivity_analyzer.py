"""
Sensitivity analysis module for barotrauma model parameters.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import spearmanr
import logging
from itertools import product

from .barotrauma_integrated_model import IntegratedBarotraumaModel
from .physiological_validator import PhysiologicalValidator

class SensitivityAnalyzer:
    """Analyze parameter sensitivity and interactions in barotrauma model."""
    
    def __init__(self, model: IntegratedBarotraumaModel):
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.phys_validator = PhysiologicalValidator()
        
        # Define parameter ranges for sensitivity analysis
        self.parameter_ranges = {
            'et_dysfunction': np.linspace(0, 1, 10),
            'V_tym': np.linspace(0.5e-3, 2.0e-3, 5),  # L
            'V_mas': np.linspace(3.0e-3, 12.0e-3, 5), # L
            'mastoid_compliance': np.logspace(-12, -9, 5),  # L/mmHg
            'climb_rate_ft_min': np.linspace(1000, 3000, 5),
            'descent_rate_ft_min': np.linspace(1000, 3000, 5)
        }
        
        # Gas exchange parameter ranges
        self.gas_exchange_ranges = {
            'O2': np.logspace(-5, -3, 5),
            'CO2': np.logspace(-5, -3, 5),
            'N2': np.logspace(-6, -4, 5),
            'H2O': np.logspace(-5, -3, 5)
        }
    
    def run_sensitivity_analysis(self, n_samples: int = 1000) -> Dict:
        """
        Perform comprehensive sensitivity analysis using Latin Hypercube Sampling.
        
        Args:
            n_samples: Number of parameter combinations to test
            
        Returns:
            Dictionary containing sensitivity analysis results
        """
        # Generate Latin Hypercube samples
        param_samples = self._generate_lhs_samples(n_samples)
        
        # Run simulations and collect results
        results = []
        for params in param_samples:
            scenario = self._create_scenario_from_params(params)
            sim_results = self.model._simulate_scenario(scenario)
            
            if sim_results:
                metrics = self._calculate_sensitivity_metrics(sim_results)
                results.append({**params, **metrics})
        
        # Calculate sensitivity indices
        sensitivity_indices = self._calculate_sensitivity_indices(pd.DataFrame(results))
        
        return {
            'parameter_effects': sensitivity_indices,
            'raw_results': results
        }
    
    def _generate_lhs_samples(self, n_samples: int) -> List[Dict]:
        """Generate Latin Hypercube samples for parameter combinations."""
        from scipy.stats import qmc
        
        # Create sampler
        sampler = qmc.LatinHypercube(d=len(self.parameter_ranges))
        samples = sampler.random(n=n_samples)
        
        # Scale samples to parameter ranges
        param_samples = []
        for sample in samples:
            params = {}
            for (param_name, param_range), value in zip(self.parameter_ranges.items(), sample):
                if param_name == 'et_dysfunction':
                    params[param_name] = value  # Already in [0,1]
                else:
                    min_val, max_val = np.min(param_range), np.max(param_range)
                    params[param_name] = min_val + value * (max_val - min_val)
            
            # Add gas exchange parameters
            params['k_MEM'] = {}
            for gas, range_vals in self.gas_exchange_ranges.items():
                idx = int(value * (len(range_vals) - 1))
                params['k_MEM'][gas] = range_vals[idx]
            
            param_samples.append(params)
        
        return param_samples
    
    def _calculate_sensitivity_metrics(self, sim_results: Dict) -> Dict:
        """Calculate key metrics for sensitivity analysis."""
        metrics = {
            'max_pressure': np.max(np.abs(sim_results['pressure_history'])),
            'volume_change': (np.max(sim_results['volume_history']) - 
                            np.min(sim_results['volume_history'])) * 1000,  # Convert to mL
            'mean_gas_exchange': np.mean(list(sim_results['gas_exchange_rates'].values())),
            'risk_score': sim_results.get('risk_score', 0)
        }
        return metrics
    
    def _calculate_sensitivity_indices(self, results_df: pd.DataFrame) -> Dict:
        """Calculate sensitivity indices using Spearman correlation."""
        output_vars = ['max_pressure', 'volume_change', 'risk_score']
        sensitivity_indices = {}
        
        for output in output_vars:
            indices = {}
            for param in self.parameter_ranges.keys():
                if param in results_df.columns:
                    corr, _ = spearmanr(results_df[param], results_df[output])
                    indices[param] = corr
            sensitivity_indices[output] = indices
        
        return sensitivity_indices
    
    def analyze_parameter_interactions(self, results: Dict) -> Dict:
        """Analyze interactions between parameters."""
        df = pd.DataFrame(results['raw_results'])
        interactions = {}
        
        # Analyze pairwise interactions
        for param1, param2 in product(self.parameter_ranges.keys(), repeat=2):
            if param1 < param2 and param1 in df.columns and param2 in df.columns:
                interaction = {
                    'correlation': df[param1].corr(df[param2]),
                    'max_pressure_effect': self._calculate_interaction_effect(
                        df, param1, param2, 'max_pressure'
                    ),
                    'risk_score_effect': self._calculate_interaction_effect(
                        df, param1, param2, 'risk_score'
                    )
                }
                interactions[f"{param1}_{param2}"] = interaction
        
        return interactions
    
    def _calculate_interaction_effect(self, df: pd.DataFrame, 
                                    param1: str, param2: str, 
                                    output: str) -> float:
        """Calculate interaction effect using regression analysis."""
        from sklearn.linear_model import LinearRegression
        
        X = df[[param1, param2]].values
        X_interaction = np.column_stack([X, X[:, 0] * X[:, 1]])
        y = df[output].values
        
        model = LinearRegression()
        model.fit(X_interaction, y)
        
        return model.coef_[2]  # Interaction coefficient
    
    def plot_sensitivity_results(self, results: Dict, save_dir: Optional[Path] = None):
        """Generate comprehensive sensitivity analysis plots."""
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Plot 1: Parameter sensitivity heatmap
        plt.figure(figsize=(12, 8))
        sensitivity_data = pd.DataFrame(results['parameter_effects'])
        sns.heatmap(sensitivity_data, annot=True, cmap='RdBu', center=0)
        plt.title('Parameter Sensitivity Analysis')
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(save_dir / 'sensitivity_heatmap.pdf')
        plt.close()
        
        # Plot 2: ET dysfunction effect
        df = pd.DataFrame(results['raw_results'])
        plt.figure(figsize=(12, 8))
        plt.scatter(df['et_dysfunction'], df['risk_score'], alpha=0.5)
        plt.xlabel('ET Dysfunction')
        plt.ylabel('Risk Score')
        plt.title('ET Dysfunction vs Risk Score')
        plt.grid(True)
        
        if save_dir:
            plt.savefig(save_dir / 'et_dysfunction_effect.pdf')
        plt.close()
        
        # Plot 3: Parameter interaction plots
        g = sns.PairGrid(df, vars=list(self.parameter_ranges.keys())[:4])
        g.map_upper(sns.scatterplot, alpha=0.1)
        g.map_lower(sns.kdeplot)
        g.map_diag(sns.histplot)
        
        if save_dir:
            plt.savefig(save_dir / 'parameter_interactions.pdf')
        plt.close()
    
    def generate_sensitivity_report(self, results: Dict, 
                                  save_path: Optional[Path] = None) -> str:
        """Generate detailed sensitivity analysis report."""
        report = ["Barotrauma Model Sensitivity Analysis", "=" * 40, ""]
        
        # Add parameter sensitivity summary
        report.extend(["Parameter Sensitivity Summary:", "-" * 30])
        for output, sensitivities in results['parameter_effects'].items():
            report.append(f"\n{output}:")
            sorted_params = sorted(sensitivities.items(), key=lambda x: abs(x[1]), reverse=True)
            for param, sensitivity in sorted_params:
                report.append(f"  {param}: {sensitivity:.3f}")
        
        # Add interaction analysis
        if 'interactions' in results:
            report.extend(["\nParameter Interactions:", "-" * 30])
            for interaction, metrics in results['interactions'].items():
                report.append(f"\n{interaction}:")
                for metric, value in metrics.items():
                    report.append(f"  {metric}: {value:.3f}")
        
        report_text = "\n".join(report)
        if save_path:
            save_path.write_text(report_text)
        
        return report_text
    
    def _create_scenario_from_params(self, params: Dict) -> Dict:
        """
        Create a complete simulation scenario from parameter set.
        
        Args:
            params: Dictionary of parameter values
            
        Returns:
            Complete scenario dictionary for simulation
        """
        # Base scenario with default values
        scenario = {
            'initial_altitude_ft': 0,
            'final_altitude_ft': 35000,
            'cruise_duration_min': 20,
            'et_dysfunction': params['et_dysfunction'],
            'V_tym': params['V_tym'],
            'V_mas': params['V_mas'],
            'mastoid_compliance': params['mastoid_compliance'],
            'climb_rate_ft_min': params['climb_rate_ft_min'],
            'descent_rate_ft_min': params['descent_rate_ft_min'],
            'k_MEM': params['k_MEM']
        }
        
        return scenario
    
    def analyze_robustness(self, n_samples: int = 500, perturbation_factor: float = 0.1) -> Dict:
        """
        Analyze model robustness to parameter perturbations.
        
        Args:
            n_samples: Number of perturbation tests
            perturbation_factor: Relative size of parameter perturbations
            
        Returns:
            Dictionary containing robustness analysis results
        """
        base_scenario = {
            'initial_altitude_ft': 0,
            'final_altitude_ft': 35000,
            'cruise_duration_min': 20,
            'et_dysfunction': 0.5,
            'V_tym': 1.0e-3,
            'V_mas': 7.75e-3,
            'mastoid_compliance': 1e-5,
            'climb_rate_ft_min': 2000,
            'descent_rate_ft_min': 2000,
            'k_MEM': {
                'O2': 0.015,
                'CO2': 0.025,
                'N2': 0.0008,
                'H2O': 0.035
            }
        }
        
        # Get base results
        base_results = self.model._simulate_scenario(base_scenario)
        if not base_results:
            raise ValueError("Base scenario simulation failed")
        
        base_metrics = self._calculate_sensitivity_metrics(base_results)
        
        # Perform perturbation analysis
        perturbation_results = []
        for _ in range(n_samples):
            perturbed_scenario = self._perturb_scenario(base_scenario, perturbation_factor)
            sim_results = self.model._simulate_scenario(perturbed_scenario)
            
            if sim_results:
                metrics = self._calculate_sensitivity_metrics(sim_results)
                perturbation_results.append({
                    'perturbation': perturbed_scenario,
                    'metrics': metrics
                })
        
        # Calculate robustness metrics
        robustness_metrics = self._calculate_robustness_metrics(
            base_metrics, perturbation_results
        )
        
        return {
            'base_metrics': base_metrics,
            'robustness_metrics': robustness_metrics,
            'perturbation_results': perturbation_results
        }
    
    def _perturb_scenario(self, scenario: Dict, factor: float) -> Dict:
        """Create perturbed version of a scenario."""
        perturbed = scenario.copy()
        
        # Perturb numerical parameters
        for param in ['et_dysfunction', 'V_tym', 'V_mas', 'mastoid_compliance',
                     'climb_rate_ft_min', 'descent_rate_ft_min']:
            if param in scenario:
                perturbed[param] = scenario[param] * (1 + np.random.uniform(-factor, factor))
        
        # Perturb gas exchange parameters
        if 'k_MEM' in scenario:
            perturbed['k_MEM'] = {
                gas: rate * (1 + np.random.uniform(-factor, factor))
                for gas, rate in scenario['k_MEM'].items()
            }
        
        return perturbed
    
    def _calculate_robustness_metrics(self, base_metrics: Dict, 
                                    perturbation_results: List[Dict]) -> Dict:
        """Calculate robustness metrics from perturbation results."""
        metrics = {}
        
        # Calculate relative changes for each metric
        for metric in base_metrics:
            changes = []
            for result in perturbation_results:
                if metric in result['metrics']:
                    relative_change = abs(
                        (result['metrics'][metric] - base_metrics[metric]) / 
                        base_metrics[metric]
                    )
                    changes.append(relative_change)
            
            if changes:
                metrics[metric] = {
                    'mean_change': np.mean(changes),
                    'std_change': np.std(changes),
                    'max_change': np.max(changes),
                    'stability_score': 1 / (1 + np.mean(changes))  # Higher is more stable
                }
        
        return metrics
    
    def plot_robustness_results(self, results: Dict, save_dir: Optional[Path] = None):
        """Generate plots for robustness analysis."""
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Plot 1: Metric variations
        plt.figure(figsize=(12, 8))
        metrics = results['robustness_metrics']
        
        metric_names = list(metrics.keys())
        stability_scores = [metrics[m]['stability_score'] for m in metric_names]
        mean_changes = [metrics[m]['mean_change'] for m in metric_names]
        
        x = np.arange(len(metric_names))
        width = 0.35
        
        plt.bar(x - width/2, stability_scores, width, label='Stability Score')
        plt.bar(x + width/2, mean_changes, width, label='Mean Change')
        
        plt.xlabel('Metrics')
        plt.ylabel('Score')
        plt.title('Model Robustness Analysis')
        plt.xticks(x, metric_names, rotation=45)
        plt.legend()
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(save_dir / 'robustness_metrics.pdf')
        plt.close()
        
        # Plot 2: Parameter sensitivity distribution
        perturbation_data = pd.DataFrame([
            result['metrics'] for result in results['perturbation_results']
        ])
        
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=perturbation_data)
        plt.xticks(rotation=45)
        plt.title('Distribution of Perturbed Results')
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(save_dir / 'perturbation_distribution.pdf')
        plt.close()
    
    def generate_robustness_report(self, results: Dict, 
                                   save_path: Optional[Path] = None) -> str:
        """Generate detailed robustness analysis report."""
        report = ["Model Robustness Analysis", "=" * 40, ""]
        
        # Add robustness metrics summary
        report.extend(["Robustness Metrics:", "-" * 20])
        for metric, values in results['robustness_metrics'].items():
            report.extend([
                f"\n{metric}:",
                f"  Stability Score: {values['stability_score']:.3f}",
                f"  Mean Change: {values['mean_change']:.3f}",
                f"  Max Change: {values['max_change']:.3f}",
                f"  Std Change: {values['std_change']:.3f}"
            ])
        
        report_text = "\n".join(report)
        if save_path:
            save_path.write_text(report_text)
        
        return report_text