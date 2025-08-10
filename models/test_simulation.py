"""
Test script for barotrauma simulation
"""

from integrated_model import IntegratedModel, SimulationConfig

def main():
    # Create test configuration
    config = SimulationConfig(
        departure_airport='MIA',  # Miami (sea level)
        destination_airport='DEN', # Denver (high altitude)
        age_months=None,          # Adult
        pathology=None            # Healthy individual
    )
    
    # Initialize model
    model = IntegratedModel(config)
    
    # Run simulation
    results = model.run_simulation()
    
    # Analyze results
    analysis = model.analyze_results(results)
    
    # Print analysis
    print("\nSimulation Results:")
    print(f"Maximum pressure differential: {analysis['max_pressure_differential']:.1f} mmHg")
    print(f"Barotitis risk: {analysis['barotitis_risk']*100:.1f}%")
    print(f"Baromyringitis risk: {analysis['baromyringitis_risk']*100:.1f}%")
    print(f"ET locked duration: {analysis['et_locked_duration']*100:.1f}% of flight")
    
    # Plot results
    model.plot_results(results)

if __name__ == "__main__":
    main() 