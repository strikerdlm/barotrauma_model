"""
Simple test script for barotrauma model parameters.
"""
import barotrauma_simulation_10
from barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile
import numpy as np

# Base physiological parameters
params = {
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

# Flight profile
flight_profile = {
    'initial_altitude_ft': 0,
    'final_altitude_ft': 35000,
    'climb_rate_ft_min': 2000,
    'descent_rate_ft_min': 2000,
    'cruise_duration_min': 10
}

def test_parameters(params, et_dysfunction=0.5):
    """Test parameters and print results."""
    scenario = {**flight_profile, **params, 'et_dysfunction': et_dysfunction}
    sim = BarotraumaSimulation(scenario)
    time_array, _, _, P_cabin_func, altitude_func = simulate_flight_profile(**flight_profile)
    result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
    
    if result is not None:
        _, P_ME_history, V_ME_history, delta_P, risk, risk_score = result
        print(f"\nTest Results (ET Dysfunction = {et_dysfunction})")
        print("-" * 50)
        print(f"Max Pressure Difference: {np.max(np.abs(delta_P)):.2f} mmHg")
        print(f"Volume Change: {(np.max(V_ME_history) - np.min(V_ME_history))*1000:.2f} mL")
        print(f"Risk Category: {risk}")
        print(f"Risk Score: {risk_score:.2f}")
        
        # Physiological checks
        volume_change = (np.max(V_ME_history) - np.min(V_ME_history))*1000
        max_pressure = np.max(np.abs(delta_P))
        
        if volume_change > 2.0:
            print(f"WARNING: Volume change ({volume_change:.2f} mL) exceeds physiological limit (2.0 mL)")
        if max_pressure > 100:
            print(f"WARNING: High pressure difference ({max_pressure:.2f} mmHg) detected")

if __name__ == "__main__":
    print("Testing Base Parameters")
    print("=" * 50)
    
    # Test with different ET dysfunction levels
    for et_level in [0.0, 0.25, 0.5, 0.75, 1.0]:
        test_parameters(params, et_dysfunction=et_level)