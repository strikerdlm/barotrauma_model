"""
Barotrauma simulation core module for unpressurized aircraft
All pressure values in mmHg, altitudes in feet, rates in ft/min
"""

import numpy as np
from typing import Dict
from .flight_profile import FlightProfile

class BarotraumaSimulation:
    """Main simulation class for barotrauma calculations.

    Includes a simple physiology-informed model for ET function and TM load.
    """
    
    # Physiological constants
    ET_LENGTH = 35.0  # mm
    ET_DIAMETER = 3.0  # mm
    
    # Base pressure thresholds
    PASSIVE_OPENING_THRESHOLD = 15.0  # mmHg - baseline passive opening
    ET_LOCK_THRESHOLD = 90.0  # mmHg - baseline ET lock
    MEMBRANE_RUPTURE_THRESHOLD = 150.0  # mmHg
    
    # Descent rate thresholds (ft/min)
    SAFE_DESCENT_RATES = {
        'normal': 10000.0,  # Normal ET can tolerate higher rates
        'mild': 2500.0,     # Mild dysfunction - much lower tolerance
        'moderate': 1500.0, # Moderate dysfunction - very sensitive
        'severe': 1000.0    # Severe dysfunction - extremely sensitive
    }
    
    # Maximum tolerable rates (ft/min)
    CRITICAL_DESCENT_RATES = {
        'normal': 18000.0,  # Normal ET maximum
        'mild': 8000.0,     # Mild dysfunction maximum
        'moderate': 4000.0, # Moderate dysfunction maximum
        'severe': 2500.0    # Severe dysfunction maximum
    }
    
    def __init__(self, flight: FlightProfile):
        """Initialize simulation with flight profile"""
        self.flight = flight
        self.initial_pressure = 760.0  # sea level pressure in mmHg
        self._configure_et_parameters()
    
    def _configure_et_parameters(self):
        """Configure ET parameters based on dysfunction level"""
        dysfunction = self.flight.et_dysfunction
        
        # Classify dysfunction severity
        if dysfunction < 0.3:
            self.severity = "normal"
            self.base_risk = 0.05  # 5% baseline risk
        elif dysfunction < 0.5:
            self.severity = "mild"
            self.base_risk = 0.15  # 15% baseline risk
        elif dysfunction < 0.7:
            self.severity = "moderate"
            self.base_risk = 0.30  # 30% baseline risk
        else:
            self.severity = "severe"
            self.base_risk = 0.50  # 50% baseline risk
        
        # Configure thresholds based on dysfunction
        self.safe_descent_rate = self.SAFE_DESCENT_RATES[self.severity]
        self.critical_descent_rate = self.CRITICAL_DESCENT_RATES[self.severity]
        
        # Pressure thresholds become more sensitive with dysfunction
        self.et_lock_threshold = self.ET_LOCK_THRESHOLD * (1.0 - 0.5 * dysfunction)
        self.passive_opening_threshold = (
            self.PASSIVE_OPENING_THRESHOLD * (1.0 + dysfunction)
        )
        
        # Risk amplification factor increases with dysfunction
        self.risk_amplification = 1.0 + (2.0 * dysfunction)  # More amplification with worse dysfunction
    
    def calculate_risk_factor(self, descent_rate: float) -> float:
        """Calculate risk factor with logarithmic scaling and amplification.

        Args:
            descent_rate: Descent rate in ft/min (positive value)

        Returns:
            Risk factor (0.0 to 1.0)
        """
        if descent_rate <= 0:
            return self.base_risk
        
        # Calculate base risk using logarithmic scaling
        if descent_rate <= self.safe_descent_rate:
            risk = self.base_risk
        else:
            # Logarithmic increase above safe rate
            excess_ratio = descent_rate / self.safe_descent_rate
            log_factor = (
                np.log(excess_ratio)
                / np.log(self.critical_descent_rate / self.safe_descent_rate)
            )
            
            # Risk increases more sharply with dysfunction
            max_additional_risk = 1.0 - self.base_risk
            risk = self.base_risk + (max_additional_risk * log_factor * self.risk_amplification)
        
        return np.clip(risk, 0.0, 1.0)
    
    def calculate_et_opening_probability(
        self, pressure_diff: float, altitude_rate: float, dt: float
    ) -> float:
        """Calculate physiologically-based ET opening probability"""
        dysfunction = self.flight.et_dysfunction
        
        # Base probability decreases with dysfunction
        base_prob = (1.0 - dysfunction) * dt
        
        # Add pressure-based probability
        if abs(pressure_diff) > self.passive_opening_threshold:
            pressure_factor = (abs(pressure_diff) / self.passive_opening_threshold - 1.0)
            base_prob += 0.1 * pressure_factor * (1.0 - dysfunction) * dt
        
        # Descent rate effect
        if altitude_rate < 0:  # Descent phase
            descent_rate = abs(altitude_rate)
            risk_factor = self.calculate_risk_factor(descent_rate)
            
            # Probability decreases more with higher risk
            base_prob *= (1.0 - risk_factor)
        
        return np.clip(base_prob, 0.0, 1.0)
    
    def run_simulation(self, dt: float = 1.0) -> Dict[str, np.ndarray]:
        """Run complete simulation with physiological parameters"""
        # Calculate total duration
        total_duration = (
            self.flight.cruise_altitude / self.flight.ascent_rate +
            self.flight.cruise_duration +
            self.flight.cruise_altitude / self.flight.descent_rate
        )
        n_steps = int(total_duration / dt)
        
        # Initialize results arrays
        results = {
            'time': np.linspace(0, total_duration, n_steps),
            'altitude': np.zeros(n_steps),
            'altitude_rate': np.zeros(n_steps),
            'P_cabin': np.zeros(n_steps),
            'P_ME': np.zeros(n_steps),
            'dP': np.zeros(n_steps),
            'ET_locked': np.zeros(n_steps, dtype=bool),
            'barotitis': np.zeros(n_steps, dtype=bool),
            'baromyringitis': np.zeros(n_steps, dtype=bool),
            'risk_factor': np.zeros(n_steps)
        }
        
        # Set initial conditions
        results['P_cabin'][0] = self.initial_pressure
        results['P_ME'][0] = self.initial_pressure
        
        # Run simulation steps
        for i in range(1, n_steps):
            time = results['time'][i]
            
            # Calculate current altitude and rate
            altitude, rate = self.flight.get_altitude_at_time(time)
            results['altitude'][i] = altitude
            results['altitude_rate'][i] = rate
            
            # Calculate cabin pressure
            results['P_cabin'][i] = self.flight.altitude_to_pressure_mmHg(altitude)
            
            # Calculate risk factor for current conditions
            if rate < 0:  # Descent phase
                risk_factor = self.calculate_risk_factor(abs(rate))
            else:
                risk_factor = self.base_risk
            
            results['risk_factor'][i] = risk_factor
            
            # Pressure differential affects ET function
            current_diff = results['P_cabin'][i] - results['P_ME'][i-1]
            
            # ET opening probability
            et_prob = self.calculate_et_opening_probability(current_diff, rate, dt)
            et_opens = np.random.random() < et_prob
            
            # Check for ET lock condition
            et_locked = (
                abs(current_diff)
                > (self.et_lock_threshold / (1.0 + risk_factor))
            )
            results['ET_locked'][i] = et_locked
            
            if et_opens and not et_locked:
                # Pressure equalization rate decreases with risk
                equalization_rate = self.PASSIVE_OPENING_THRESHOLD * (1.0 - risk_factor) * dt
                equalization = np.clip(current_diff, -equalization_rate, equalization_rate)
                results['P_ME'][i] = results['P_ME'][i-1] + equalization
            else:
                # No equalization
                results['P_ME'][i] = results['P_ME'][i-1]
            
            # Calculate pressure differential
            results['dP'][i] = results['P_ME'][i] - results['P_cabin'][i]
            
            # Barotrauma conditions adjusted by risk factor
            threshold_factor = 1.0 / (1.0 + risk_factor)
            results['barotitis'][i] = abs(results['dP'][i]) > (self.et_lock_threshold * threshold_factor)
            results['baromyringitis'][i] = (
                abs(results['dP'][i])
                > (self.MEMBRANE_RUPTURE_THRESHOLD * threshold_factor)
            )
        
        return results