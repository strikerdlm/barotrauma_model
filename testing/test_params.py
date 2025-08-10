"""
Test script for barotrauma model parameters with physiologically accurate values.
"""
import numpy as np
from barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile

def test_parameters(params, et_dysfunction=0.5):
    """Test a single parameter set and return results."""
    flight_profile = {
        'initial_altitude_ft': 0,
        'final_altitude_ft': 35000,
        'climb_rate_ft_min': 2000,
        'descent_rate_ft_min': 2000,
        'cruise_duration_min': 10
    }
    
    scenario = {**flight_profile, **params, 'et_dysfunction': et_dysfunction}
    sim = BarotraumaSimulation(scenario)
    
    time_array, _, _, P_cabin_func, altitude_func = simulate_flight_profile(**flight_profile)
    result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
    
    if result is not None:
        _, P_ME_history, V_ME_history, delta_P, risk, risk_score = result
        metrics = {
            'max_pressure_diff': np.max(np.abs(delta_P)),
            'volume_change': np.max(V_ME_history) - np.min(V_ME_history),
            'risk': risk,
            'risk_score': risk_score
        }
        
        print(f"Max Pressure Difference: {metrics['max_pressure_diff']:.2f} mmHg")
        print(f"Volume Change: {metrics['volume_change']*1000:.2f} mL")
        print(f"Risk Category: {metrics['risk']}")
        print(f"Risk Score: {metrics['risk_score']:.2f}")
        
        if metrics['volume_change']*1000 > 2.0:
            print("WARNING: Volume change exceeds physiological limit of 2.0 mL")
        if metrics['max_pressure_diff'] > 100:
            print("WARNING: High pressure difference detected")
        
        return metrics
    return None

if __name__ == "__main__":
    # Base parameters (physiologically accurate)
    base_params = {
        'R_A': 0.3,  # Moderate ET tube resistance
        'T_A': 0.1,  # Standard time constant
        'P_ET_open': 8,  # Typical opening pressure (mmHg)
        'P_ET_close': 0,  # Standard closing pressure
        'k_MEM': {
            'O2': 0.015,  # Moderate O2 exchange rate
            'CO2': 0.025,  # Moderate CO2 exchange rate
            'N2': 0.0008,  # Low N2 exchange rate
            'H2O': 0.035   # Moderate H2O exchange rate
        },
        'V_tym': 1.5e-3,  # Typical tympanic volume (L)
        'V_mas': 7.75e-3,  # Standard mastoid volume (L)
        'mastoid_compliance': 2e-5  # Moderate compliance
    }
    
    # Conservative parameters (less aggressive)
    conservative_params = {
        'R_A': 0.2,  # Lower resistance
        'T_A': 0.1,
        'P_ET_open': 6,  # Lower opening pressure
        'P_ET_close': 0,
        'k_MEM': {
            'O2': 0.012,
            'CO2': 0.022,
            'N2': 0.0006,
            'H2O': 0.032
        },
        'V_tym': 1.2e-3,
        'V_mas': 7.75e-3,
        'mastoid_compliance': 1.5e-5
    }
    
    # Progressive parameters (more aggressive but still physiological)
    progressive_params = {
        'R_A': 0.4,  # Higher resistance
        'T_A': 0.1,
        'P_ET_open': 10,  # Higher opening pressure
        'P_ET_close': 0,
        'k_MEM': {
            'O2': 0.018,
            'CO2': 0.028,
            'N2': 0.001,
            'H2O': 0.038
        },
        'V_tym': 1.8e-3,
        'V_mas': 7.75e-3,
        'mastoid_compliance': 2.5e-5
    }
    
    # Test each parameter set
    print("\nTesting Conservative Parameters:")
    print("-" * 30)
    test_parameters(conservative_params)
    
    print("\nTesting Base Parameters:")
    print("-" * 30)
    test_parameters(base_params)
    
    print("\nTesting Progressive Parameters:")
    print("-" * 30)
    test_parameters(progressive_params)
    
    # Test with different ET dysfunction levels
    print("\nTesting Base Parameters with Different ET Dysfunction Levels:")
    print("-" * 50)
    for et_level in [0.0, 0.25, 0.5, 0.75, 1.0]:
        print(f"\nET Dysfunction Level: {et_level:.2f}")
        print("-" * 30)
        test_parameters(base_params, et_dysfunction=et_level) 