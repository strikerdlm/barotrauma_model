"""
Integrated Middle Ear Model
Based on Kanick & Doyle (2005) - J Appl Physiol 98: 1592-1602

This module provides the high-level interface for running middle ear
barotrauma simulations with different conditions and parameters.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt

from physiology import PhysiologyParameters, AgeRelatedParameters, PathologicalConditions
from et import ETParameters
from alveolar import AlveolarParameters
from barotrauma_simulation import BarotraumaSimulation
from flight_profile import FlightProfile

@dataclass
class SimulationConfig:
    """Configuration for simulation runs"""
    ascent_rate: float = 2500.0  # feet/min (typical rapid ascent)
    descent_rate: float = 3000.0  # feet/min (can be up to 18000 ft/min)
    cruise_altitude: float = 35000.0  # feet
    cruise_duration: float = 120.0  # minutes
    et_dysfunction: float = 0.0  # 0-1 scale
    age_months: Optional[int] = None
    pathology: Optional[str] = None
    pathology_severity: Optional[float] = None
    
    def get_flight_profile(self) -> FlightProfile:
        """Create flight profile"""
        return FlightProfile(
            ascent_rate=self.ascent_rate,
            descent_rate=self.descent_rate,
            cruise_altitude=self.cruise_altitude,
            cruise_duration=self.cruise_duration,
            et_dysfunction=self.et_dysfunction
        )

class IntegratedModel:
    """High-level interface for middle ear barotrauma simulation"""
    
    def __init__(self, config: SimulationConfig):
        """Initialize model with configuration"""
        self.config = config
        
        # Setup base parameters
        self.physiology = PhysiologyParameters()
        self.et = ETParameters()
        self.alveolar = AlveolarParameters()
        
        # Apply age-related modifications if specified
        if config.age_months is not None:
            age_params = AgeRelatedParameters(config.age_months)
            self._apply_age_parameters(age_params)
            
        # Apply pathological conditions if specified
        if config.pathology is not None:
            self._apply_pathology()
            
    def _apply_age_parameters(self, age_params: AgeRelatedParameters):
        """Apply age-specific parameter modifications"""
        params = age_params.parameters
        self.et.compliance *= params['tm_compliance']
        # Apply other age-related parameter modifications
        
    def _apply_pathology(self):
        """Apply pathological condition modifications"""
        if self.config.pathology == 'et_obstruction':
            self.physiology = PathologicalConditions.et_obstruction(self.physiology)
        elif self.config.pathology == 'poor_mtvp':
            self.physiology = PathologicalConditions.poor_mtvp_function(
                self.physiology, self.config.pathology_severity or 0.5)
        elif self.config.pathology == 'hypercompliant_tm':
            self.physiology = PathologicalConditions.hypercompliant_tm(self.physiology)
            
    def run_simulation(self) -> Dict[str, np.ndarray]:
        """Run complete simulation"""
        flight_profile = self.config.get_flight_profile()
        simulation = BarotraumaSimulation(flight_profile)
        return simulation.run_simulation()
    
    def analyze_results(self, results: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Analyze simulation results"""
        analysis = {
            'max_pressure_differential': np.max(np.abs(results['dP'])),
            'barotitis_risk': np.mean(results['barotitis']),
            'baromyringitis_risk': np.mean(results['baromyringitis']),
            'et_locked_duration': np.mean(results['ET_locked']),
            'max_altitude_rate': np.max(np.abs(results['altitude_rate']))
        }
        return analysis
    
    def plot_results(self, results: Dict[str, np.ndarray]):
        """Plot simulation results"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot pressure differentials
        ax1.plot(results['time'], results['dP'])
        ax1.axhline(y=90, color='r', linestyle='--', label='ET Lock Threshold')
        ax1.axhline(y=100, color='r', linestyle=':', label='Membrane Rupture Threshold')
        ax1.set_xlabel('Time (min)')
        ax1.set_ylabel('ΔP (mmHg)')
        ax1.legend()
        ax1.grid(True)
        
        # Plot pathological conditions
        ax2.plot(results['time'], results['barotitis'], label='Barotitis')
        ax2.plot(results['time'], results['baromyringitis'], label='Baromyringitis')
        ax2.plot(results['time'], results['ET_locked'], label='ET Locked')
        ax2.set_xlabel('Time (min)')
        ax2.set_ylabel('Condition Present')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()