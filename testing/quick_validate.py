"""
Comprehensive validation tests for advanced physiological middle ear model.
"""

import numpy as np
import matplotlib.pyplot as plt
from core.barotrauma_simulation_10 import AdvancedPhysiologicalMEModel, PhysiologicalParameters

def test_volume_effects():
    """Test the effects of different mastoid volumes on pressure regulation."""
    print("\nTesting mastoid volume effects...")
    
    volumes = [4.0, 7.75, 12.0, 15.0]  # Different mastoid volumes (ml)
    duration = 10 * 60  # 10 minutes
    # Use 2-second timesteps instead of 1ms
    t = np.arange(0, duration, 2)  # 2-second timesteps
    start_alt = 25000
    
    def altitude_func(t_val):
        progress = t_val / duration
        return start_alt * (1 - min(progress, 1.0))
    
    print("\nMastoid Volume Effects:")
    print("-" * 100)
    print(f"{'Volume (ml)':<15} | {'Max ΔP':<10} | {'TM Disp':<10} | {'ET Opens':<10} | {'Buffer Cap':<12} | {'Risk':<10}")
    print("-" * 100)
    
    plt.figure(figsize=(10, 6))
    
    for vol in volumes:
        params = PhysiologicalParameters()
        params.Vmas = vol
        sim = AdvancedPhysiologicalMEModel({'et_dysfunction': 0.0})
        sim.params.Vmas = vol
        
        result = sim.simulate_flight(t, altitude_func)
        
        # Calculate metrics
        max_delta_P = np.max(np.abs(result['delta_P']))
        delta_P_h2o = max_delta_P * 13.6
        
        # TM displacement
        CTM = sim.tm_compliance(delta_P_h2o)
        tm_displacement = (delta_P_h2o * CTM * params.ATM) / 1000.0
        tm_displacement = np.clip(tm_displacement, -params.max_TM_displacement, params.max_TM_displacement)
        
        # ET openings (adjusted for 2s timesteps)
        et_openings = sum(np.abs(result['delta_P']) > params.ET_passive_threshold/13.6)
        
        # Buffer capacity
        theoretical_delta_P = 760 - sim.calculate_pressure_mmHg(start_alt)
        buffer_capacity = (1 - max_delta_P/theoretical_delta_P) * 100
        
        risk_level = result['risk'][-1]
        
        print(f"{vol:<15.1f} | {max_delta_P:>8.1f}  | {tm_displacement:>8.3f} | {et_openings:>8d} | {buffer_capacity:>10.1f}% | {risk_level:>8s}")
        
        plt.plot(t/60, result['delta_P'], label=f'Vmas = {vol} ml')
    
    plt.xlabel('Time (minutes)')
    plt.ylabel('Pressure Differential (mmHg)')
    plt.title('Pressure Regulation with Different Mastoid Volumes')
    plt.legend()
    plt.grid(True)
    plt.show()

def test_descent_rates():
    """Test the model's response to different descent rates."""
    print("\nTesting descent rate effects...")
    
    rates = [2000, 4000, 8000, 12000, 18000]  # ft/min
    duration = 10 * 60  # 10 minutes
    # Use 2-second timesteps
    t = np.arange(0, duration, 2)
    start_alt = 25000
    
    print("\nDescent Rate Effects:")
    print("-" * 110)
    print(f"{'Rate (ft/min)':<15} | {'Max ΔP':<10} | {'TM Disp':<10} | {'ET Opens':<10} | {'Comp Eff':<12} | {'Risk':<10}")
    print("-" * 110)
    
    plt.figure(figsize=(10, 6))
    
    for rate in rates:
        def altitude_func(t_val):
            target_time = start_alt / rate  # Time to reach ground at this rate
            progress = min(t_val / target_time, 1.0)
            return start_alt * (1 - progress)
        
        # Test with both healthy and dysfunctional ET
        for dysfunction in [0.0, 0.6]:
            sim = AdvancedPhysiologicalMEModel({'et_dysfunction': dysfunction})
            result = sim.simulate_flight(t, altitude_func)
            
            # Calculate metrics
            max_delta_P = np.max(np.abs(result['delta_P']))
            delta_P_h2o = max_delta_P * 13.6
            
            # TM displacement
            CTM = sim.tm_compliance(delta_P_h2o)
            tm_displacement = (delta_P_h2o * CTM * sim.params.ATM) / 1000.0
            
            # ET openings (adjusted for 2s timesteps)
            et_openings = sum(np.abs(result['delta_P']) > sim.params.ET_passive_threshold/13.6)
            
            # Compensation efficiency
            theoretical_delta_P = 760 - sim.calculate_pressure_mmHg(start_alt)
            comp_efficiency = (1 - max_delta_P/theoretical_delta_P) * 100
            
            risk_level = result['risk'][-1]
            
            status = "Healthy" if dysfunction == 0.0 else "Dysfunctional"
            print(f"{rate:<15d} | {max_delta_P:>8.1f}  | {tm_displacement:>8.3f} | {et_openings:>8d} | "
                  f"{comp_efficiency:>10.1f}% | {risk_level:>8s} ({status})")
            
            label = f'{rate} ft/min ({status})'
            plt.plot(t/60, result['delta_P'], label=label, 
                    linestyle='-' if dysfunction == 0.0 else '--')
    
    plt.xlabel('Time (minutes)')
    plt.ylabel('Pressure Differential (mmHg)')
    plt.title('Pressure Regulation at Different Descent Rates')
    plt.legend()
    plt.grid(True)
    plt.show()

def test_gas_exchange():
    """Test gas exchange dynamics and O2/CO2 balance."""
    print("\nTesting gas exchange dynamics...")
    
    duration = 10 * 60  # 10 minutes
    # Use 2-second timesteps
    t = np.arange(0, duration, 2)
    start_alt = 25000
    
    def altitude_func(t_val):
        progress = t_val / duration
        return start_alt * (1 - min(progress, 1.0))
    
    print("\nGas Exchange Analysis:")
    print("-" * 120)
    print(f"{'Condition':<20} | {'O2 Change':<10} | {'CO2 Change':<10} | {'N2 Change':<10} | {'O2/CO2':<10} | {'Exchange Rate':<12}")
    print("-" * 120)
    
    plt.figure(figsize=(12, 8))
    
    # Test different ET dysfunction levels
    dysfunctions = [0.0, 0.3, 0.6, 0.9]
    
    for dysfunction in dysfunctions:
        sim = AdvancedPhysiologicalMEModel({'et_dysfunction': dysfunction})
        result = sim.simulate_flight(t, altitude_func)
        
        # Calculate gas changes (adjusted for 2s timesteps)
        O2_change = np.mean(np.diff(result['P_O2'])) * 2  # Scale by timestep
        CO2_change = np.mean(np.diff(result['P_CO2'])) * 2
        N2_change = np.mean(np.diff(result['P_N2'])) * 2
        O2_CO2_ratio = np.mean(result['P_O2']) / np.mean(result['P_CO2'])
        
        # Calculate overall gas exchange rate
        total_exchange = np.abs(O2_change) + np.abs(CO2_change) + np.abs(N2_change)
        
        status = f"ET Dysf: {dysfunction:.1f}"
        print(f"{status:<20} | {O2_change:>8.2f}  | {CO2_change:>8.2f}  | {N2_change:>8.2f}  | "
              f"{O2_CO2_ratio:>8.2f}  | {total_exchange:>10.2f}")
        
        # Plot gas partial pressures
        plt.subplot(2, 2, 1)
        plt.plot(t/60, result['P_O2'], label=f'ET Dysf: {dysfunction}')
        plt.title('O2 Partial Pressure')
        plt.xlabel('Time (minutes)')
        plt.ylabel('mmHg')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 2)
        plt.plot(t/60, result['P_CO2'], label=f'ET Dysf: {dysfunction}')
        plt.title('CO2 Partial Pressure')
        plt.xlabel('Time (minutes)')
        plt.ylabel('mmHg')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 3)
        plt.plot(t/60, result['P_N2'], label=f'ET Dysf: {dysfunction}')
        plt.title('N2 Partial Pressure')
        plt.xlabel('Time (minutes)')
        plt.ylabel('mmHg')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 2, 4)
        plt.plot(t/60, result['P_O2']/result['P_CO2'], label=f'ET Dysf: {dysfunction}')
        plt.title('O2/CO2 Ratio')
        plt.xlabel('Time (minutes)')
        plt.ylabel('Ratio')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def run_all_tests():
    """Run all validation tests."""
    print("Starting comprehensive validation of physiological middle ear model...")
    
    # Test volume effects
    test_volume_effects()
    
    # Test descent rates
    test_descent_rates()
    
    # Test gas exchange
    test_gas_exchange()
    
    print("\nValidation complete.")

if __name__ == "__main__":
    run_all_tests() 