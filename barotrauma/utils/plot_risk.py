"""
Script to visualize ET dysfunction vs barotrauma risk relationship.
"""
import os
import sys

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import numpy as np
import matplotlib.pyplot as plt
from src.barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile

# Physiologically accurate parameters
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

def simulate_with_dysfunction(et_dysfunction):
    """Run simulation with given ET dysfunction level."""
    scenario = {**flight_profile, **params, 'et_dysfunction': et_dysfunction}
    sim = BarotraumaSimulation(scenario)
    time_array, _, _, P_cabin_func, altitude_func = simulate_flight_profile(**flight_profile)
    result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
    
    if result is not None:
        _, P_ME_history, V_ME_history, delta_P, risk, risk_score = result
        return {
            'max_pressure_diff': np.max(np.abs(delta_P)),
            'volume_change': np.max(V_ME_history) - np.min(V_ME_history),
            'risk': risk,
            'risk_score': risk_score,
            'P_ME_history': P_ME_history,
            'delta_P': delta_P,
            'time': time_array
        }
    return None

def main():
    # Test range of ET dysfunction values
    et_values = np.linspace(0, 1, 21)  # 21 points from 0 to 1
    results = []
    
    print("Running simulations...")
    for et in et_values:
        result = simulate_with_dysfunction(et)
        if result:
            results.append(result)
            print(f"ET Dysfunction: {et:.2f}, Risk Score: {result['risk_score']:.2f}, "
                  f"Max Pressure Diff: {result['max_pressure_diff']:.2f} mmHg")
    
    # Extract data for plotting
    risk_scores = [r['risk_score'] for r in results]
    pressure_diffs = [r['max_pressure_diff'] for r in results]
    volume_changes = [r['volume_change']*1000 for r in results]  # Convert to mL
    
    # Create visualization
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Risk Score vs ET Dysfunction
    plt.subplot(2, 2, 1)
    plt.plot(et_values, risk_scores, 'b-', linewidth=2)
    plt.fill_between(et_values, risk_scores, alpha=0.2)
    plt.xlabel('ET Dysfunction Level')
    plt.ylabel('Risk Score')
    plt.title('Risk Score vs ET Dysfunction')
    plt.grid(True)
    
    # Plot 2: Max Pressure Difference vs ET Dysfunction
    plt.subplot(2, 2, 2)
    plt.plot(et_values, pressure_diffs, 'r-', linewidth=2)
    plt.axhline(y=100, color='r', linestyle='--', alpha=0.5, label='High Risk Threshold')
    plt.xlabel('ET Dysfunction Level')
    plt.ylabel('Max Pressure Difference (mmHg)')
    plt.title('Maximum Pressure Difference vs ET Dysfunction')
    plt.grid(True)
    plt.legend()
    
    # Plot 3: Volume Change vs ET Dysfunction
    plt.subplot(2, 2, 3)
    plt.plot(et_values, volume_changes, 'g-', linewidth=2)
    plt.axhline(y=2.0, color='r', linestyle='--', alpha=0.5, label='Physiological Limit')
    plt.xlabel('ET Dysfunction Level')
    plt.ylabel('Volume Change (mL)')
    plt.title('Middle Ear Volume Change vs ET Dysfunction')
    plt.grid(True)
    plt.legend()
    
    # Plot 4: Pressure History for selected dysfunction levels
    plt.subplot(2, 2, 4)
    selected_levels = [0.0, 0.5, 1.0]
    for i, et in enumerate(selected_levels):
        result = results[int(et * 20)]  # Index into our results
        plt.plot(result['time'], result['delta_P'], 
                label=f'ET Dysfunction = {et:.1f}',
                linewidth=2)
    plt.xlabel('Time (minutes)')
    plt.ylabel('Pressure Difference (mmHg)')
    plt.title('Pressure Difference Over Time')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('et_dysfunction_analysis.png')
    plt.show()
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("-" * 50)
    print(f"Minimum Risk Score: {min(risk_scores):.2f}")
    print(f"Maximum Risk Score: {max(risk_scores):.2f}")
    print(f"Minimum Pressure Difference: {min(pressure_diffs):.2f} mmHg")
    print(f"Maximum Pressure Difference: {max(pressure_diffs):.2f} mmHg")
    print(f"Minimum Volume Change: {min(volume_changes):.2f} mL")
    print(f"Maximum Volume Change: {max(volume_changes):.2f} mL")

if __name__ == "__main__":
    main() 