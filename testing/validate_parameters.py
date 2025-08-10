"""
Streamlined parameter validation module for barotrauma simulation.
"""

import os
import sys
import numpy as np
import logging

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class ParameterValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Simplified flight profile
        self.test_profile = {
            'initial_altitude_ft': 0,
            'final_altitude_ft': 35000,
            'climb_rate_ft_min': 2000,
            'descent_rate_ft_min': 2000,
            'cruise_duration_min': 10
        }
        
        # Original parameters
        self.original_params = {
            'R_A': 0.1,
            'T_A': 0.1,
            'P_ET_open': 5,
            'P_ET_close': 0,
            'k_MEM': {'O2': 0.01, 'CO2': 0.02, 'N2': 0.001, 'H2O': 0.03},
            'V_tym': 1.0e-3,
            'V_mas': 7.75e-3,
            'mastoid_compliance': 1e-5
        }
        
        # Adjusted parameters
        self.adjusted_params = {
            'R_A': 1.0,
            'T_A': 0.1,
            'P_ET_open': 15,
            'P_ET_close': 0,
            'k_MEM': {'O2': 0.02, 'CO2': 0.03, 'N2': 0.0005, 'H2O': 0.04},
            'V_tym': 2.0e-3,
            'V_mas': 7.75e-3,
            'mastoid_compliance': 5e-5
        }
    
    def quick_validation(self, et_dysfunction=0.5):
        """Run a quick validation comparing original and adjusted parameters."""
        self.logger.info("\nRunning quick validation...")
        
        for param_set, params in [('Original', self.original_params), 
                                ('Adjusted', self.adjusted_params)]:
            # Setup simulation
            scenario = {
                **self.test_profile,
                **params,
                'et_dysfunction': et_dysfunction
            }
            sim = BarotraumaSimulation(scenario)
            
            # Run simulation
            time_array, _, _, P_cabin_func, altitude_func = \
                simulate_flight_profile(**self.test_profile)
            
            result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
            
            if result is not None:
                _, P_ME_history, V_ME_history, delta_P, risk, risk_score = result
                
                # Calculate key metrics
                max_pressure_diff = np.max(np.abs(delta_P))
                volume_change = np.max(V_ME_history) - np.min(V_ME_history)
                
                self.logger.info(f"\n{param_set} Parameters Results:")
                self.logger.info(f"Max Pressure Difference: {max_pressure_diff:.2f} mmHg")
                self.logger.info(f"Volume Change: {volume_change*1000:.2f} mL")
                self.logger.info(f"Risk Category: {risk}")
                self.logger.info(f"Risk Score: {risk_score:.2f}")
                
                # Evaluate physiological constraints
                if volume_change > 0.002:
                    self.logger.warning(f"Volume change ({volume_change*1000:.2f} mL) exceeds typical physiological limit (2.0 mL)")
                
                if max_pressure_diff > 100:
                    self.logger.warning(f"Pressure difference ({max_pressure_diff:.2f} mmHg) is high")

def main():
    setup_logging()
    validator = ParameterValidator()
    validator.quick_validation()

if __name__ == "__main__":
    main() 