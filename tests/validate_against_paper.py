"""
Validation Tests
Compares model predictions against results from Kanick & Doyle (2005)
"""

import numpy as np
import matplotlib.pyplot as plt
from models.barotrauma_simulation import BarotraumaSimulation, FlightProfile
from models.physiology import PhysiologyParameters, PathologicalConditions
from models.et import ETParameters
from models.alveolar import AlveolarParameters

def validate_figure_3():
    """Validate against Figure 3 from paper - pressure chamber experiment"""
    # Setup parameters from paper
    physiology = PhysiologyParameters()
    et = ETParameters(
        P_ME_ET_O=292,  # mmH2O
        P_C=136,        # mmH2O
        mTVP_force=1.0
    )
    flight = FlightProfile(
        departure_elevation=0,
        destination_elevation=0,
        cruise_elevation=1920,  # ft/min for 25s
        cruise_duration=25/60   # 25 seconds
    )
    
    # Run simulation
    simulation = BarotraumaSimulation(
        physiology=physiology,
        et=et,
        alveolar=AlveolarParameters(),
        flight=flight
    )
    
    results = simulation.run_simulation(
        dt=0.001,
        swallowing_frequency=33*60  # 33 swallows/min
    )
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(results['time'], results['dP'], 'b-', label='Model')
    # Add paper data points here for comparison
    plt.xlabel('Time (s)')
    plt.ylabel('ΔP_ME-cabin (mmH2O)')
    plt.title('Validation against Figure 3')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return results

def validate_figure_5():
    """Validate against Figure 5 from paper - different ET conditions"""
    # Test conditions from paper
    conditions = {
        'normal': PhysiologyParameters(),
        'blocked': PathologicalConditions.et_obstruction(PhysiologyParameters()),
        'poor_mtvp': PathologicalConditions.poor_mtvp_function(
            PhysiologyParameters(), 
            severity=0.9
        )
    }
    
    # Flight profile (PIT-MIA)
    flight = FlightProfile(
        departure_elevation=1204,  # PIT
        destination_elevation=8,    # MIA
        cruise_duration=170.0
    )
    
    results = {}
    for condition, physiology in conditions.items():
        simulation = BarotraumaSimulation(
            physiology=physiology,
            et=ETParameters(),
            alveolar=AlveolarParameters(),
            flight=flight
        )
        results[condition] = simulation.run_simulation()
    
    # Plot results
    plt.figure(figsize=(12, 8))
    for condition, result in results.items():
        plt.plot(result['time'], result['dP'], label=condition)
    
    plt.axhline(y=250, color='r', linestyle='--', label='Barotitis Threshold')
    plt.axhline(y=1300, color='r', linestyle=':', label='Baromyringitis Threshold')
    plt.xlabel('Time (min)')
    plt.ylabel('ΔP_ME-cabin (mmH2O)')
    plt.title('Validation against Figure 5')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return results

def validate_figure_7():
    """Validate against Figure 7 from paper - buffering mechanisms"""
    # Test different VME and RA combinations
    vme_values = [1, 4, 7, 10, 13, 16]  # ml
    ra_values = np.linspace(0, 40, 20)   # mmHg/cc/min
    
    results = {}
    for vme in vme_values:
        results[vme] = []
        for ra in ra_values:
            # Modify parameters
            physiology = PhysiologyParameters()
            et = ETParameters(compliance=ra)
            
            # Run simulation
            simulation = BarotraumaSimulation(
                physiology=physiology,
                et=et,
                alveolar=AlveolarParameters(),
                flight=FlightProfile(
                    departure_elevation=1204,  # PIT
                    destination_elevation=8,    # MIA
                    cruise_duration=170.0
                )
            )
            
            result = simulation.run_simulation()
            results[vme].append(np.max(np.abs(result['dP'])))
    
    # Plot results
    plt.figure(figsize=(10, 6))
    for vme, tpgs in results.items():
        plt.plot(ra_values, tpgs, label=f'VME = {vme} ml')
    
    plt.xlabel('RA (mmHg/cc/min)')
    plt.ylabel('Terminal Pressure Gradient (mmH2O)')
    plt.title('Validation against Figure 7A')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return results

if __name__ == "__main__":
    # Run validations
    print("Validating against Figure 3...")
    fig3_results = validate_figure_3()
    
    print("\nValidating against Figure 5...")
    fig5_results = validate_figure_5()
    
    print("\nValidating against Figure 7...")
    fig7_results = validate_figure_7() 