"""
Validation tests for barotrauma simulation model.
"""

import numpy as np
import matplotlib.pyplot as plt
from core.barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile

def validate_descent_rates():
    """Test model behavior at different descent rates for healthy and ET dysfunction cases."""
    
    # Test parameters
    descent_rates = [2000, 8000, 12000, 18000]  # ft/min
    dysfunction_levels = [0.0, 0.5, 1.0]  # 0=healthy, 0.5=moderate, 1.0=severe
    
    # Flight profile parameters
    initial_altitude = 25000  # ft
    final_altitude = 0  # ft
    climb_rate = 2000  # ft/min
    cruise_duration = 10  # min
    
    # Results storage
    max_pressure_diffs = np.zeros((len(dysfunction_levels), len(descent_rates)))
    success_rates = np.zeros((len(dysfunction_levels), len(descent_rates)))
    
    # Run simulations
    n_trials = 5  # Multiple trials per condition
    
    for i, et_dysfunction in enumerate(dysfunction_levels):
        for j, descent_rate in enumerate(descent_rates):
            successes = 0
            max_pressures = []
            
            for _ in range(n_trials):
                # Create simulation
                params = {
                    'et_dysfunction': et_dysfunction,
                    'V_tym': 1.0e-3,
                    'V_mas': 7.75e-3
                }
                sim = BarotraumaSimulation(params)
                
                # Generate flight profile
                time_array, _, _, P_cabin_func, altitude_func = simulate_flight_profile(
                    initial_altitude,
                    final_altitude,
                    climb_rate,
                    descent_rate,
                    cruise_duration
                )
                
                # Run simulation
                result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
                
                if result is not None:
                    _, _, _, delta_P, risk_category, _ = result
                    max_pressure = np.max(np.abs(delta_P))
                    max_pressures.append(max_pressure)
                    
                    # Consider successful if max pressure difference is below threshold
                    if max_pressure < 100 and risk_category != "High":
                        successes += 1
            
            success_rates[i, j] = successes / n_trials
            max_pressure_diffs[i, j] = np.mean(max_pressures) if max_pressures else float('nan')
            
            # Print progress
            print(f"\nResults for ET dysfunction {et_dysfunction:.1f} at descent rate {descent_rate} ft/min:")
            print(f"Success rate: {success_rates[i,j]:.2f}")
            print(f"Average max pressure: {max_pressure_diffs[i,j]:.1f} mmHg")
    
    # Plot results
    plt.figure(figsize=(12, 8))
    
    # Success rates plot
    plt.subplot(2, 1, 1)
    for i, dysfunction in enumerate(dysfunction_levels):
        plt.plot(descent_rates, success_rates[i], 
                marker='o', 
                label=f'ET Dysfunction = {dysfunction}')
    
    plt.xlabel('Descent Rate (ft/min)')
    plt.ylabel('Success Rate')
    plt.title('Success Rate vs Descent Rate')
    plt.grid(True)
    plt.legend()
    
    # Max pressure differences plot
    plt.subplot(2, 1, 2)
    for i, dysfunction in enumerate(dysfunction_levels):
        plt.plot(descent_rates, max_pressure_diffs[i], 
                marker='o', 
                label=f'ET Dysfunction = {dysfunction}')
    
    plt.xlabel('Descent Rate (ft/min)')
    plt.ylabel('Max Pressure Difference (mmHg)')
    plt.title('Maximum Pressure Difference vs Descent Rate')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('validation_results.png')
    plt.close()
    
    # Print summary results
    print("\nValidation Results Summary:")
    print("\nSuccess Rates:")
    print("Descent Rate (ft/min) |", end=" ")
    for rate in descent_rates:
        print(f"{rate:8d} |", end=" ")
    print("\n" + "-"*60)
    
    for i, dysfunction in enumerate(dysfunction_levels):
        print(f"ET Dysfunction {dysfunction:.1f}    |", end=" ")
        for j in range(len(descent_rates)):
            print(f"{success_rates[i,j]:8.2f} |", end=" ")
        print()
    
    print("\nMax Pressure Differences (mmHg):")
    print("Descent Rate (ft/min) |", end=" ")
    for rate in descent_rates:
        print(f"{rate:8d} |", end=" ")
    print("\n" + "-"*60)
    
    for i, dysfunction in enumerate(dysfunction_levels):
        print(f"ET Dysfunction {dysfunction:.1f}    |", end=" ")
        for j in range(len(descent_rates)):
            print(f"{max_pressure_diffs[i,j]:8.1f} |", end=" ")
        print()

if __name__ == "__main__":
    print("Starting validation test...")
    validate_descent_rates()
    print("\nValidation test complete.") 