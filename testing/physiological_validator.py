"""
Specialized validator for physiological aspects of the barotrauma model.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

class PhysiologicalValidator:
    """Validator for physiological constraints and relationships."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define physiological constraints based on literature
        self.constraints = {
            'pressure': {
                'barotitis_threshold': 18,    # mmHg (from literature)
                'baromyringitis_threshold': 95,# mmHg (from literature)
                'max_sustainable': 200,        # mmHg (physiological limit)
                'normal_range': (-10, 10)      # mmHg (normal fluctuation)
            },
            'volume': {
                'tympanic_range': (0.5e-3, 2.0e-3),  # L
                'mastoid_range': (3.0e-3, 12.0e-3),  # L
                'max_change_rate': 0.1e-3,    # L/s
            },
            'gas_exchange': {
                'O2_range': (0.005, 0.025),   # mol/s
                'CO2_range': (0.015, 0.035),  # mol/s
                'N2_range': (0.0005, 0.002),  # mol/s
                'H2O_range': (0.025, 0.045)   # mol/s
            },
            'et_function': {
                'opening_pressure': (5, 15),   # mmHg
                'closing_pressure': (-5, 5),   # mmHg
                'active_duration': (0.05, 0.2) # s
            }
        }
    
    def validate_pressure_dynamics(self, 
                                 pressure_history: np.ndarray, 
                                 time_array: np.ndarray) -> Dict:
        """
        Validate pressure changes against physiological constraints.
        
        Args:
            pressure_history: Array of pressure values over time
            time_array: Corresponding time points
            
        Returns:
            Dictionary containing validation results
        """
        # Calculate key metrics
        pressure_rate = np.gradient(pressure_history, time_array)
        max_pressure = np.max(np.abs(pressure_history))
        max_rate = np.max(np.abs(pressure_rate))
        
        # Check against constraints
        results = {
            'within_max_limit': max_pressure <= self.constraints['pressure']['max_sustainable'],
            'barotitis_risk': max_pressure > self.constraints['pressure']['barotitis_threshold'],
            'baromyringitis_risk': max_pressure > self.constraints['pressure']['baromyringitis_threshold'],
            'pressure_rate_valid': max_rate < 50,  # mmHg/s (physiological limit)
            'metrics': {
                'max_pressure': max_pressure,
                'max_rate': max_rate,
                'mean_pressure': np.mean(pressure_history),
                'pressure_std': np.std(pressure_history)
            }
        }
        
        return results
    
    def validate_volume_changes(self, 
                              volume_history: np.ndarray,
                              time_array: np.ndarray) -> Dict:
        """Validate volume changes against physiological constraints."""
        volume_rate = np.gradient(volume_history, time_array)
        
        results = {
            'within_range': np.all((volume_history >= self.constraints['volume']['tympanic_range'][0]) & 
                                 (volume_history <= self.constraints['volume']['mastoid_range'][1])),
            'rate_valid': np.all(np.abs(volume_rate) <= self.constraints['volume']['max_change_rate']),
            'metrics': {
                'max_volume': np.max(volume_history),
                'min_volume': np.min(volume_history),
                'max_rate': np.max(np.abs(volume_rate))
            }
        }
        
        return results
    
    def validate_gas_exchange(self, gas_exchange_rates: Dict[str, float]) -> Dict:
        """Validate gas exchange rates against physiological constraints."""
        results = {gas: {} for gas in gas_exchange_rates}
        
        for gas, rate in gas_exchange_rates.items():
            range_key = f'{gas}_range'
            if range_key in self.constraints['gas_exchange']:
                min_rate, max_rate = self.constraints['gas_exchange'][range_key]
                results[gas] = {
                    'within_range': min_rate <= rate <= max_rate,
                    'value': rate
                }
        
        return results
    
    def plot_physiological_validation(self, 
                                    validation_data: Dict,
                                    save_dir: Optional[Path] = None):
        """Generate plots for physiological validation results."""
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Pressure dynamics plot
        plt.figure(figsize=(12, 8))
        time = validation_data['time']
        pressure = validation_data['pressure_history']
        
        plt.plot(time, pressure, 'b-', label='Pressure')
        plt.axhline(y=self.constraints['pressure']['barotitis_threshold'], 
                   color='y', linestyle='--', label='Barotitis Threshold')
        plt.axhline(y=self.constraints['pressure']['baromyringitis_threshold'],
                   color='r', linestyle='--', label='Baromyringitis Threshold')
        
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (mmHg)')
        plt.title('Pressure Dynamics Validation')
        plt.legend()
        plt.grid(True)
        
        if save_dir:
            plt.savefig(save_dir / 'pressure_validation.pdf')
        plt.close()
        
        # Volume changes plot
        if 'volume_history' in validation_data:
            plt.figure(figsize=(12, 8))
            volume = validation_data['volume_history']
            
            plt.plot(time, volume * 1000, 'g-', label='Volume')  # Convert to mL
            plt.axhline(y=self.constraints['volume']['tympanic_range'][0] * 1000,
                       color='r', linestyle='--', label='Min Volume')
            plt.axhline(y=self.constraints['volume']['mastoid_range'][1] * 1000,
                       color='r', linestyle='--', label='Max Volume')
            
            plt.xlabel('Time (s)')
            plt.ylabel('Volume (mL)')
            plt.title('Volume Changes Validation')
            plt.legend()
            plt.grid(True)
            
            if save_dir:
                plt.savefig(save_dir / 'volume_validation.pdf')
            plt.close()
    
    def generate_physiological_report(self, 
                                    validation_results: Dict,
                                    save_path: Optional[Path] = None) -> str:
        """Generate detailed report of physiological validation."""
        report = ["Physiological Validation Report", "=" * 40, ""]
        
        # Pressure dynamics
        if 'pressure' in validation_results:
            pressure_results = validation_results['pressure']
            report.extend([
                "Pressure Dynamics:",
                "-" * 20,
                f"Maximum Pressure: {pressure_results['metrics']['max_pressure']:.1f} mmHg",
                f"Maximum Rate: {pressure_results['metrics']['max_rate']:.1f} mmHg/s",
                f"Within Limits: {'Yes' if pressure_results['within_max_limit'] else 'No'}",
                f"Barotitis Risk: {'Yes' if pressure_results['barotitis_risk'] else 'No'}",
                f"Baromyringitis Risk: {'Yes' if pressure_results['baromyringitis_risk'] else 'No'}",
                ""
            ])
        
        # Volume changes
        if 'volume' in validation_results:
            volume_results = validation_results['volume']
            report.extend([
                "Volume Changes:",
                "-" * 20,
                f"Maximum Volume: {volume_results['metrics']['max_volume']*1000:.2f} mL",
                f"Minimum Volume: {volume_results['metrics']['min_volume']*1000:.2f} mL",
                f"Within Range: {'Yes' if volume_results['within_range'] else 'No'}",
                f"Rate Valid: {'Yes' if volume_results['rate_valid'] else 'No'}",
                ""
            ])
        
        # Gas exchange
        if 'gas_exchange' in validation_results:
            gas_results = validation_results['gas_exchange']
            report.extend(["Gas Exchange Rates:", "-" * 20])
            for gas, results in gas_results.items():
                report.append(f"{gas}: {results['value']:.6f} mol/s "
                            f"({'Valid' if results['within_range'] else 'Invalid'})")
        
        report_text = "\n".join(report)
        if save_path:
            save_path.write_text(report_text)
        
        return report_text 