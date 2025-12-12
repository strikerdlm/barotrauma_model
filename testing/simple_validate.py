"""
Simple validation script for barotrauma model parameters.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

# Ensure project root is importable when running as a script/module.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.barotrauma_simulation_10 import (  # noqa: E402
    BarotraumaSimulation,
    simulate_flight_profile,
)


def validate_single_flight(params: dict, et_dysfunction: float = 0.5) -> dict | None:
    """Run a single flight simulation and return key metrics."""
    # Basic flight profile
    flight_profile = {
        'initial_altitude_ft': 0,
        'final_altitude_ft': 35000,
        'climb_rate_ft_min': 2000,
        'descent_rate_ft_min': 2000,
        'cruise_duration_min': 10
    }
    
    # Setup simulation
    scenario = {**flight_profile, **params, 'et_dysfunction': et_dysfunction}
    sim = BarotraumaSimulation(scenario)
    
    # Run simulation
    time_array, _, _, P_cabin_func, altitude_func = simulate_flight_profile(**flight_profile)
    result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
    
    if result is not None:
        _, P_ME_history, V_ME_history, delta_P, risk, risk_score = result
        return {
            'max_pressure_diff': np.max(np.abs(delta_P)),
            'volume_change': np.max(V_ME_history) - np.min(V_ME_history),
            'risk': risk,
            'risk_score': risk_score
        }
    return None

def main():
    # Original parameters
    original_params = {
        'R_A': 0.1,
        'T_A': 0.1,
        'P_ET_open': 5,
        'P_ET_close': 0,
        'k_MEM': {'O2': 0.01, 'CO2': 0.02, 'N2': 0.001, 'H2O': 0.03},
        'V_tym': 1.0e-3,
        'V_mas': 7.75e-3,
        'mastoid_compliance': 1e-5
    }
    
    # Intermediate parameters
    intermediate_params = {
        'R_A': 0.5,  # Reduced from 1.0
        'T_A': 0.1,
        'P_ET_open': 10,  # Reduced from 15
        'P_ET_close': 0,
        'k_MEM': {'O2': 0.02, 'CO2': 0.03, 'N2': 0.0005, 'H2O': 0.04},  # Keeping improved gas exchange
        'V_tym': 2.0e-3,
        'V_mas': 7.75e-3,
        'mastoid_compliance': 2.5e-5  # Reduced from 5e-5
    }
    
    # Previous adjusted parameters
    adjusted_params = {
        'R_A': 1.0,
        'T_A': 0.1,
        'P_ET_open': 15,
        'P_ET_close': 0,
        'k_MEM': {'O2': 0.02, 'CO2': 0.03, 'N2': 0.0005, 'H2O': 0.04},
        'V_tym': 2.0e-3,
        'V_mas': 7.75e-3,
        'mastoid_compliance': 5e-5
    }
    
    # Test all parameter sets
    param_sets = [
        ("Original", original_params),
        ("Intermediate", intermediate_params),
        ("Previous Adjusted", adjusted_params)
    ]
    
    for name, params in param_sets:
        print(f"\nTesting {name} Parameters:")
        print("-" * 30)
        result = validate_single_flight(params)
        if result:
            print(f"Max Pressure Difference: {result['max_pressure_diff']:.2f} mmHg")
            print(f"Volume Change: {result['volume_change']*1000:.2f} mL")
            print(f"Risk Category: {result['risk']}")
            print(f"Risk Score: {result['risk_score']:.2f}")
            
            # Add warnings for concerning values
            if result['volume_change']*1000 > 2.0:
                print(f"WARNING: Volume change exceeds physiological limit of 2.0 mL")
            if result['max_pressure_diff'] > 100:
                print(f"WARNING: High pressure difference detected")

if __name__ == "__main__":
    main() 