"""
Validation Tests for Middle Ear Barotrauma Model
Compares simulation results against Kanick & Doyle (2005) data
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
import pytest

from models.barotrauma_simulation import BarotraumaSimulation, FlightProfile
from models.physiology import PhysiologyParameters
from models.et import ETParameters
from models.alveolar import AlveolarParameters

# Load validation data from paper
VALIDATION_DATA_PATH = Path(__file__).parent / 'data' / 'paper_validation.json'

def load_validation_data():
    """Load validation data from JSON file"""
    with open(VALIDATION_DATA_PATH, 'r') as f:
        return json.load(f)

class TestModelValidation:
    """Validation test suite"""
    
    @pytest.fixture
    def paper_data(self):
        """Load paper validation data"""
        return load_validation_data()
    
    @pytest.fixture
    def base_simulation(self):
        """Create base simulation setup"""
        physiology = PhysiologyParameters()
        et = ETParameters(
            P_ME_ET_O=350,  # mmH2O
            P_C=100,        # mmH2O
            mTVP_force=1.0
        )
        flight = FlightProfile(
            departure_elevation=1204,  # PIT
            destination_elevation=8,    # MIA
            cruise_duration=170.0
        )
        
        return BarotraumaSimulation(
            physiology=physiology,
            et=et,
            alveolar=AlveolarParameters(),
            flight=flight
        )
    
    def test_pressure_chamber_validation(self, base_simulation, paper_data):
        """
        Validate against pressure chamber experiment 
        (Figure 3 in paper)
        """
        # Run simulation
        results = base_simulation.run_simulation(
            dt=1/30,  # 2 seconds
            swallowing_frequency=33*60  # 33 swallows/min as in paper
        )
        
        # Compare with paper data
        paper_pressure = np.array(paper_data['pressure_chamber']['pressure'])
        paper_time = np.array(paper_data['pressure_chamber']['time'])
        
        # Interpolate simulation results to match paper time points
        from scipy.interpolate import interp1d
        sim_interp = interp1d(results['time'], results['dP'])
        sim_pressure = sim_interp(paper_time)
        
        # Calculate error metrics
        rmse = np.sqrt(np.mean((sim_pressure - paper_pressure)**2))
        max_error = np.max(np.abs(sim_pressure - paper_pressure))
        
        # Plot comparison
        plt.figure(figsize=(10, 6))
        plt.plot(paper_time, paper_pressure, 'ko-', label='Paper Data')
        plt.plot(results['time'], results['dP'], 'b-', label='Simulation')
        plt.xlabel('Time (s)')
        plt.ylabel('ΔP_ME-cabin (mmH2O)')
        plt.title('Pressure Chamber Validation\n'
                 f'RMSE: {rmse:.1f} mmH2O, Max Error: {max_error:.1f} mmH2O')
        plt.legend()
        plt.grid(True)
        plt.savefig('validation_pressure_chamber.png')
        
        # Assert validation criteria
        assert rmse < 50.0, f"RMSE too high: {rmse:.1f} mmH2O"
        assert max_error < 100.0, f"Max error too high: {max_error:.1f} mmH2O"
    
    def test_pathological_conditions(self, base_simulation, paper_data):
        """
        Validate pathological conditions 
        (Figure 5 in paper)
        """
        # Test conditions
        conditions = {
            'normal': PhysiologyParameters(),
            'blocked': PhysiologyParameters(
                k_O2=0, k_CO2=0, k_N2=0  # Complete blockage
            ),
            'poor_mtvp': PhysiologyParameters(
                k_O2=0.002, k_CO2=0.04, k_N2=0.0002  # Reduced function
            )
        }
        
        results = {}
        for condition, params in conditions.items():
            sim = base_simulation
            sim.physiology = params
            results[condition] = sim.run_simulation()
        
        # Compare with paper data
        for condition in conditions:
            paper_data_cond = np.array(paper_data['pathological'][condition])
            sim_data = results[condition]['dP']
            
            # Calculate error metrics
            rmse = np.sqrt(np.mean((sim_data - paper_data_cond)**2))
            
            # Plot comparison
            plt.figure(figsize=(10, 6))
            plt.plot(paper_data['pathological']['time'], paper_data_cond, 
                    'ko-', label='Paper Data')
            plt.plot(results[condition]['time'], sim_data, 
                    'b-', label='Simulation')
            plt.xlabel('Time (min)')
            plt.ylabel('ΔP_ME-cabin (mmH2O)')
            plt.title(f'{condition.capitalize()} Condition Validation\n'
                     f'RMSE: {rmse:.1f} mmH2O')
            plt.legend()
            plt.grid(True)
            plt.savefig(f'validation_{condition}.png')
            
            # Assert validation criteria
            assert rmse < 100.0, f"RMSE too high for {condition}: {rmse:.1f} mmH2O"
    
    def test_buffering_mechanisms(self, base_simulation, paper_data):
        """
        Validate buffering mechanisms 
        (Figure 7 in paper)
        """
        from scipy.interpolate import interp1d

        # Test different VME and RA combinations
        vme_values = [1, 4, 7, 10, 13, 16]  # ml
        ra_values = np.linspace(0, 40, 20)   # mmHg/cc/min
        
        results = {}
        for vme in vme_values:
            results[vme] = []
            for ra in ra_values:
                # Modify parameters
                et = ETParameters(compliance=ra)
                sim = base_simulation
                sim.et = et
                # Ensure the simulator can observe the VME sweep.
                sim.physiology.V_ME_ml = float(vme)
                
                result = sim.run_simulation()
                # Use terminal pressure gradient (signed) for comparison.
                results[vme].append(float(result["dP"][-1]))
        
        # Compare with paper data
        paper_results = paper_data['buffering']
        
        plt.figure(figsize=(10, 6))
        for vme in vme_values:
            plt.plot(ra_values, results[vme], 'b-', label=f'Sim VME={vme}')
            plt.plot(paper_results['RA'], paper_results[f'VME_{vme}'], 
                    'ko--', label=f'Paper VME={vme}')
        
        plt.xlabel('RA (mmHg/cc/min)')
        plt.ylabel('Terminal Pressure Gradient (mmH2O)')
        plt.title('Buffering Mechanisms Validation')
        plt.legend()
        plt.grid(True)
        plt.savefig('validation_buffering.png')
        
        # Calculate overall error
        total_rmse = 0
        n_points = 0
        for vme in vme_values:
            sim_interp = interp1d(ra_values, results[vme])
            paper_ra = np.array(paper_results['RA'])
            paper_values = np.array(paper_results[f'VME_{vme}'])
            sim_values = sim_interp(paper_ra)
            
            rmse = np.sqrt(np.mean((sim_values - paper_values)**2))
            total_rmse += rmse
            n_points += len(paper_ra)
        
        avg_rmse = total_rmse / len(vme_values)
        assert avg_rmse < 150.0, f"Average RMSE too high: {avg_rmse:.1f} mmH2O"

def run_validation_tests():
    """Run all validation tests"""
    pytest.main(['-v', __file__])

if __name__ == "__main__":
    run_validation_tests() 