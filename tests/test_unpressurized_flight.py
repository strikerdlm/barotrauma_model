"""
Test cases for barotrauma risk in unpressurized aircraft
Based on Kanick & Doyle (2005) - J Appl Physiol 98: 1592-1602

Tests different descent rates and ET dysfunction scenarios in unpressurized flight conditions.
"""

import pytest
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

from models.barotrauma_simulation import BarotraumaSimulation, FlightProfile
from models.physiology import PhysiologyParameters, PathologicalConditions
from models.et import ETParameters
from models.alveolar import AlveolarParameters

@dataclass
class UnpressurizedFlightProfile:
    """Extended flight profile for unpressurized aircraft"""
    descent_rate: float  # feet/min - required, so listed first
    max_altitude: float = 25000.0  # feet
    cruise_altitude: float = 25000.0  # feet
    cruise_duration: float = 10.0  # minutes
    ascent_duration: float = 15.0  # minutes
    departure_elevation: float = 0.0  # feet
    destination_elevation: float = 0.0  # feet
    
    def calculate_cabin_pressure(self, time: float, initial_pressure: float) -> float:
        """
        Calculate cabin pressure for unpressurized flight
        
        Args:
            time: Current time in simulation
            initial_pressure: Ground level pressure
            
        Returns:
            Current cabin pressure
        """
        # Standard atmosphere equation
        if time < self.ascent_duration:
            # Ascent phase
            altitude = (time / self.ascent_duration) * self.max_altitude
        elif time < self.ascent_duration + self.cruise_duration:
            # Cruise phase
            altitude = self.cruise_altitude
        else:
            # Descent phase
            descent_time = time - (self.ascent_duration + self.cruise_duration)
            altitude = max(0, self.cruise_altitude - descent_time * self.descent_rate/60)
            
        # Calculate pressure using standard atmosphere equation
        P0 = 760  # mmHg at sea level
        T0 = 288.15  # K
        L = 0.0065  # K/m
        g = 9.81  # m/s^2
        M = 0.0289644  # kg/mol
        R = 8.31447  # J/(mol·K)
        
        h = altitude * 0.3048  # Convert feet to meters
        P = P0 * (1 - L*h/T0)**(g*M/(R*L))
        
        return P

@pytest.fixture
def descent_rates() -> List[float]:
    """Define descent rates to test"""
    return [1000, 2000, 5000, 10000, 18000]  # feet/min

@pytest.fixture
def et_dysfunction_scenarios() -> List[Dict]:
    """Define ET dysfunction scenarios"""
    return [
        {
            'name': 'complete_obstruction',
            'params': {'et_obstruction': True}
        },
        {
            'name': 'severe_mtvp_dysfunction',
            'params': {'poor_mtvp': True, 'severity': 0.9}
        },
        {
            'name': 'moderate_mtvp_dysfunction',
            'params': {'poor_mtvp': True, 'severity': 0.5}
        }
    ]

def test_unpressurized_descent_rates(descent_rates, et_dysfunction_scenarios):
    """Test barotrauma risk for different descent rates with ET dysfunction"""
    
    results = {}
    for rate in descent_rates:
        results[rate] = {}
        
        for scenario in et_dysfunction_scenarios:
            # Setup flight profile
            flight = UnpressurizedFlightProfile(
                departure_elevation=0,
                destination_elevation=0,
                descent_rate=rate
            )
            
            # Setup physiology with ET dysfunction
            physiology = PhysiologyParameters()
            if scenario['params'].get('et_obstruction'):
                physiology = PathologicalConditions.et_obstruction(physiology)
            elif scenario['params'].get('poor_mtvp'):
                physiology = PathologicalConditions.poor_mtvp_function(
                    physiology, 
                    scenario['params']['severity']
                )
            
            # Run simulation
            simulation = BarotraumaSimulation(
                physiology=physiology,
                et=ETParameters(),
                alveolar=AlveolarParameters(),
                flight=flight
            )
            
            sim_results = simulation.run_simulation(dt=0.01)
            
            # Calculate risk metrics
            results[rate][scenario['name']] = {
                'barotitis_risk': np.mean(sim_results['barotitis']),
                'baromyringitis_risk': np.mean(sim_results['baromyringitis']),
                'max_pressure_differential': np.max(np.abs(sim_results['dP'])),
                'et_locked_duration': np.mean(sim_results['ET_locked']),
                'time_to_symptoms': _calculate_time_to_symptoms(sim_results)
            }
    
    # Verify expected relationships
    for scenario in et_dysfunction_scenarios:
        scenario_name = scenario['name']
        
        # Risk should increase with descent rate
        risks = [results[rate][scenario_name]['barotitis_risk'] 
                for rate in descent_rates]
        assert all(risks[i] <= risks[i+1] for i in range(len(risks)-1))
        
        # Complete obstruction should be worse than dysfunction
        if scenario_name != 'complete_obstruction':
            for rate in descent_rates:
                assert (results[rate]['complete_obstruction']['baromyringitis_risk'] >=
                       results[rate][scenario_name]['baromyringitis_risk'])

def _calculate_time_to_symptoms(results: Dict) -> float:
    """Calculate time until barotrauma symptoms appear"""
    if not np.any(results['barotitis']):
        return float('inf')
    return results['time'][np.where(results['barotitis'])[0][0]]

def test_altitude_effects():
    """Test effect of maximum altitude on barotrauma risk"""
    altitudes = [15000, 20000, 25000, 30000]  # feet
    descent_rate = 5000  # feet/min
    
    results = {}
    for alt in altitudes:
        flight = UnpressurizedFlightProfile(
            departure_elevation=0,
            destination_elevation=0,
            max_altitude=alt,
            cruise_altitude=alt,
            descent_rate=descent_rate
        )
        
        # Test with moderate ET dysfunction
        physiology = PathologicalConditions.poor_mtvp_function(
            PhysiologyParameters(), 
            severity=0.5
        )
        
        simulation = BarotraumaSimulation(
            physiology=physiology,
            et=ETParameters(),
            alveolar=AlveolarParameters(),
            flight=flight
        )
        
        sim_results = simulation.run_simulation(dt=0.01)
        
        results[alt] = {
            'barotitis_risk': np.mean(sim_results['barotitis']),
            'max_pressure_differential': np.max(np.abs(sim_results['dP']))
        }
    
    # Risk should increase with altitude
    risks = [results[alt]['barotitis_risk'] for alt in altitudes]
    assert all(risks[i] <= risks[i+1] for i in range(len(risks)-1))

def test_descent_profile_effects(descent_rates):
    """Test effect of different descent profiles on barotrauma risk"""
    
    def stepped_descent(rate: float) -> UnpressurizedFlightProfile:
        """Create stepped descent profile"""
        return UnpressurizedFlightProfile(
            departure_elevation=0,
            destination_elevation=0,
            descent_rate=rate,
            # Add pauses every 5000 ft
            descent_pauses=[(20000, 2), (15000, 2), (10000, 2), (5000, 2)]
        )
    
    def continuous_descent(rate: float) -> UnpressurizedFlightProfile:
        """Create continuous descent profile"""
        return UnpressurizedFlightProfile(
            departure_elevation=0,
            destination_elevation=0,
            descent_rate=rate
        )
    
    results = {}
    for rate in descent_rates:
        # Compare stepped vs continuous descent
        profiles = {
            'stepped': stepped_descent(rate),
            'continuous': continuous_descent(rate)
        }
        
        results[rate] = {}
        for profile_name, flight in profiles.items():
            # Test with moderate ET dysfunction
            physiology = PathologicalConditions.poor_mtvp_function(
                PhysiologyParameters(), 
                severity=0.5
            )
            
            simulation = BarotraumaSimulation(
                physiology=physiology,
                et=ETParameters(),
                alveolar=AlveolarParameters(),
                flight=flight
            )
            
            sim_results = simulation.run_simulation(dt=0.01)
            
            results[rate][profile_name] = {
                'barotitis_risk': np.mean(sim_results['barotitis']),
                'max_pressure_differential': np.max(np.abs(sim_results['dP']))
            }
    
    # Stepped descent should have lower risk
    for rate in descent_rates:
        assert (results[rate]['stepped']['barotitis_risk'] <
                results[rate]['continuous']['barotitis_risk']) 