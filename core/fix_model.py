"""
Script to fix common model issues and improve stability.
"""

import numpy as np
from pathlib import Path
import logging
from typing import Dict, Optional, Tuple
import json

from barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/model_fixes.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def optimize_solver_parameters(sim: BarotraumaSimulation) -> Dict:
    """Optimize solver parameters for better stability."""
    best_params = {
        'rtol': 1e-6,
        'atol': 1e-8,
        'max_step': 0.1,
        'method': 'RK45'
    }
    
    # Test different solver configurations
    test_configs = [
        {'rtol': 1e-6, 'atol': 1e-8, 'method': 'RK45'},
        {'rtol': 1e-8, 'atol': 1e-10, 'method': 'RK45'},
        {'rtol': 1e-6, 'atol': 1e-8, 'method': 'BDF'},
        {'rtol': 1e-8, 'atol': 1e-10, 'method': 'BDF'}
    ]
    
    best_stability = 0
    time_array, _, _, P_cabin_func, altitude_func = simulate_flight_profile(0, 35000, 2000, 1500, 120)
    
    for config in test_configs:
        sim.solver_params = config
        try:
            result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
            if result is not None:
                _, P_ME, V_ME, _, _, _ = result
                stability = assess_stability(P_ME, V_ME)
                if stability > best_stability:
                    best_stability = stability
                    best_params = config.copy()
        except Exception:
            continue
    
    return best_params

def assess_stability(P_ME: np.ndarray, V_ME: np.ndarray) -> float:
    """Assess numerical stability of simulation results."""
    stability_score = 1.0
    
    # Check for NaN/Inf values
    if np.any(np.isnan(P_ME)) or np.any(np.isnan(V_ME)) or \
       np.any(np.isinf(P_ME)) or np.any(np.isinf(V_ME)):
        return 0.0
    
    # Check for physiological bounds
    if np.any(np.abs(P_ME) > 200) or np.any(V_ME <= 0) or np.any(V_ME > 20e-3):
        stability_score *= 0.5
    
    # Check for smoothness
    P_ME_diff = np.diff(P_ME)
    V_ME_diff = np.diff(V_ME)
    
    if np.any(np.abs(P_ME_diff) > 1000):
        stability_score *= 0.7
    
    if np.any(np.abs(V_ME_diff) > 1e-3):
        stability_score *= 0.7
    
    return stability_score

def adjust_et_parameters(params: Dict) -> Dict:
    """Adjust ET parameters for better physiological response."""
    et_dysfunction = params.get('et_dysfunction', 0.0)
    
    # More gradual effect of dysfunction
    base_resistance = 0.1
    adjusted_params = params.copy()
    
    # Resistance increases with dysfunction but with diminishing returns
    adjusted_params['R_A'] = base_resistance * (1 + np.tanh(2 * et_dysfunction))
    
    # Opening time decreases with dysfunction
    adjusted_params['T_A'] = params.get('T_A', 0.1) * (1 - 0.5 * et_dysfunction)
    
    # Pressure thresholds adjust with dysfunction
    adjusted_params['P_ET_open'] = params.get('P_ET_open', 5) * (1 + 0.3 * et_dysfunction)
    adjusted_params['P_ET_close'] = params.get('P_ET_close', -5) * (1 + 0.3 * et_dysfunction)
    
    return adjusted_params

def fix_gas_exchange_rates(params: Dict) -> Dict:
    """Fix gas exchange rates to ensure stability."""
    adjusted_params = params.copy()
    
    # Base rates with physiological constraints
    base_rates = {
        'O2': (0.015, 0.005, 0.025),
        'CO2': (0.025, 0.015, 0.035),
        'N2': (0.0008, 0.0005, 0.002),
        'H2O': (0.035, 0.025, 0.045)
    }
    
    if 'k_MEM' not in adjusted_params:
        adjusted_params['k_MEM'] = {}
    
    for gas, (base, min_val, max_val) in base_rates.items():
        current = adjusted_params['k_MEM'].get(gas, base)
        adjusted_params['k_MEM'][gas] = np.clip(current, min_val, max_val)
    
    return adjusted_params

def apply_model_fixes(params: Dict) -> Tuple[Dict, Dict]:
    """Apply all model fixes and return optimized parameters."""
    logger = setup_logging()
    logger.info("Starting model fixes")
    
    try:
        # Step 1: Adjust ET parameters
        logger.info("Adjusting ET parameters")
        fixed_params = adjust_et_parameters(params)
        
        # Step 2: Fix gas exchange rates
        logger.info("Fixing gas exchange rates")
        fixed_params = fix_gas_exchange_rates(fixed_params)
        
        # Step 3: Create simulation with fixed parameters
        sim = BarotraumaSimulation(fixed_params)
        
        # Step 4: Optimize solver parameters
        logger.info("Optimizing solver parameters")
        solver_params = optimize_solver_parameters(sim)
        
        # Save fixed parameters
        Path("results").mkdir(exist_ok=True)
        with open("results/fixed_parameters.json", "w") as f:
            json.dump({
                "model_parameters": fixed_params,
                "solver_parameters": solver_params
            }, f, indent=4)
        
        logger.info("Model fixes completed successfully")
        return fixed_params, solver_params
        
    except Exception as e:
        logger.error(f"Model fixing failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Test parameters
    test_params = {
        'et_dysfunction': 0.5,
        'V_tym': 1.0e-3,
        'V_mas': 7.75e-3,
        'k_MEM': {
            'O2': 0.015,
            'CO2': 0.025,
            'N2': 0.0008,
            'H2O': 0.035
        }
    }
    
    fixed_params, solver_params = apply_model_fixes(test_params) 