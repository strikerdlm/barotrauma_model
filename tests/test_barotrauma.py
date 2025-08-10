"""
Test cases for barotrauma simulation
"""

import pytest
import numpy as np
from models.barotrauma_simulation import BarotraumaSimulation, FlightProfile
from models.physiology import PhysiologyParameters
from models.et import ETParameters
from models.alveolar import AlveolarParameters

@pytest.fixture
def simulation():
    """Create basic simulation setup"""
    physiology = PhysiologyParameters()
    et = ETParameters()
    alveolar = AlveolarParameters()
    flight = FlightProfile(
        departure_elevation=1204,  # PIT
        destination_elevation=8,    # MIA
        cruise_duration=170.0
    )
    
    return BarotraumaSimulation(physiology, et, alveolar, flight)

def test_pressure_calculation(simulation):
    """Test basic pressure calculations"""
    # Test membrane exchange
    dP = simulation._calculate_membrane_exchange(760, 760, 0.001)
    assert isinstance(dP, float)
    assert abs(dP) < 1.0  # Should be small for short time step
    
    # Test passive opening
    assert simulation._should_open_passively(1200, 760)  # Large positive differential
    assert not simulation._should_open_passively(760, 760)  # No differential
    
    # Test active opening probability
    n_trials = 1000
    active_openings = sum(
        simulation._should_open_actively(0, 5.2)  # Normal swallowing frequency
        for _ in range(n_trials)
    )
    expected_rate = 5.2 / 3600 * n_trials
    assert abs(active_openings - expected_rate) < 3 * np.sqrt(expected_rate)  # Within 3 std dev

def test_flight_simulation(simulation):
    """Test complete flight simulation"""
    results = simulation.run_simulation(dt=0.01)
    
    # Check results structure
    assert 'time' in results
    assert 'P_cabin' in results
    assert 'P_ME' in results
    assert 'dP' in results
    assert 'ET_locked' in results
    assert 'barotitis' in results
    assert 'baromyringitis' in results
    
    # Check basic properties
    assert len(results['time']) > 100
    assert not np.any(np.isnan(results['P_ME']))
    assert not np.any(np.isnan(results['dP']))
    
    # Check pressure bounds
    assert np.all(results['P_cabin'] > 0)
    assert np.all(results['P_ME'] > 0)
    
    # Check pathological conditions
    assert np.any(results['barotitis'])  # Should occur at some point
    assert np.sum(results['baromyringitis']) <= np.sum(results['barotitis'])  # More severe

def test_pathological_conditions(simulation):
    """Test simulation with pathological conditions"""
    # Test ET obstruction
    simulation.physiology.k_O2 = 0
    simulation.physiology.k_CO2 = 0
    simulation.physiology.k_N2 = 0
    
    results = simulation.run_simulation(dt=0.01)
    assert np.any(results['ET_locked'])  # Should get locked
    assert np.any(results['baromyringitis'])  # Should cause severe condition
    
    # Test poor mTVP function
    simulation = BarotraumaSimulation(
        PhysiologyParameters(),
        ETParameters(mTVP_force=0.1),  # Reduced muscle force
        AlveolarParameters(),
        simulation.flight
    )
    
    results = simulation.run_simulation(dt=0.01)
    assert np.sum(results['barotitis']) > 0  # Should have increased risk 