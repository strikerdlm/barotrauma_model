"""
Simple script to plot ET dysfunction vs barotrauma risk.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from src.barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile

# Base parameters
params = {
    'R_A': 0.3,
    'T_A': 0.1,
    'P_ET_open': 8,
    'P_ET_close': 0,
    'k_MEM': {'O2': 0.015, 'CO2': 0.025, 'N2': 0.0008, 'H2O': 0.035},
    'V_tym': 1.5e-3,
    'V_mas': 7.75e-3,
    'mastoid_compliance': 2e-5
}

# Flight profile
flight_profile = {
    'initial_altitude_ft': 0,
    'final_altitude_ft': 35000,
    'climb_rate_ft_min': 2000,
    'descent_rate_ft_min': 2000,
    'cruise_duration_min': 10
}

print("Running simulations...")
et_values = np.linspace(0, 1, 11)  # Test 11 points from 0 to 1
risk_scores = []
pressure_diffs = []

for et in et_values:
    # Run simulation
    scenario = {**flight_profile, **params, 'et_dysfunction': et}
    sim = BarotraumaSimulation(scenario)
    time_array, _, _, P_cabin_func, altitude_func = simulate_flight_profile(**flight_profile)
    result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
    
    if result is not None:
        _, _, _, delta_P, risk, risk_score = result
        risk_scores.append(risk_score)
        pressure_diffs.append(np.max(np.abs(delta_P)))
        print(f"ET Dysfunction: {et:.1f}, Risk Score: {risk_score:.2f}, "
              f"Max Pressure Diff: {np.max(np.abs(delta_P)):.2f} mmHg")

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(et_values, risk_scores, 'b-o', linewidth=2, label='Risk Score')
plt.plot(et_values, np.array(pressure_diffs)/100, 'r--o', linewidth=2, 
         label='Max Pressure Diff (scaled)')

plt.xlabel('ET Dysfunction Level')
plt.ylabel('Risk Score / Normalized Pressure')
plt.title('ET Dysfunction vs Barotrauma Risk')
plt.grid(True)
plt.legend()

plt.savefig('et_risk_analysis.png')
plt.show()

print("\nAnalysis complete. Results saved to 'et_risk_analysis.png'") 