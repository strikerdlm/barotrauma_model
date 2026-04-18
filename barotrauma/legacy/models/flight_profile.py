"""
Flight profile class for barotrauma simulation
Defines the flight characteristics and ET dysfunction parameters
"""

import numpy as np

class FlightProfile:
    """Flight profile with ET dysfunction parameter"""
    
    def __init__(self, 
                 cruise_altitude: float,
                 ascent_rate: float,
                 descent_rate: float,
                 cruise_duration: float,
                 et_dysfunction: float):
        """
        Initialize flight profile
        
        Args:
            cruise_altitude: Target cruise altitude in feet
            ascent_rate: Rate of climb in feet/minute
            descent_rate: Rate of descent in feet/minute
            cruise_duration: Duration at cruise altitude in minutes
            et_dysfunction: ET dysfunction level (0.0 to 1.0)
        """
        self.cruise_altitude = cruise_altitude
        self.ascent_rate = ascent_rate
        self.descent_rate = descent_rate
        self.cruise_duration = cruise_duration
        self.et_dysfunction = et_dysfunction
        
        # Validate parameters
        if not 0.0 <= et_dysfunction <= 1.0:
            raise ValueError("ET dysfunction must be between 0.0 and 1.0")
        if cruise_altitude <= 0:
            raise ValueError("Cruise altitude must be positive")
        if ascent_rate <= 0 or descent_rate <= 0:
            raise ValueError("Rates must be positive")
        if cruise_duration < 0:
            raise ValueError("Cruise duration must be non-negative")
    
    def get_altitude_at_time(self, time: float) -> tuple[float, float]:
        """
        Calculate altitude and rate of change at given time
        
        Args:
            time: Time in minutes from takeoff
            
        Returns:
            Tuple of (altitude in feet, rate of change in feet/minute)
        """
        # Calculate phase transition times
        ascent_time = self.cruise_altitude / self.ascent_rate
        cruise_end_time = ascent_time + self.cruise_duration
        total_time = cruise_end_time + self.cruise_altitude / self.descent_rate
        
        # Determine flight phase and calculate altitude
        if time <= ascent_time:  # Climbing
            altitude = self.ascent_rate * time
            rate = self.ascent_rate
        elif time <= cruise_end_time:  # Cruise
            altitude = self.cruise_altitude
            rate = 0.0
        elif time <= total_time:  # Descending
            descent_time = time - cruise_end_time
            altitude = self.cruise_altitude - (self.descent_rate * descent_time)
            rate = -self.descent_rate
        else:  # Flight completed
            altitude = 0.0
            rate = 0.0
        
        return altitude, rate
    
    def altitude_to_pressure_mmHg(self, altitude: float) -> float:
        """
        Convert altitude to pressure in mmHg using standard atmosphere model
        
        Args:
            altitude: Altitude in feet
            
        Returns:
            Pressure in mmHg
        """
        # Standard atmosphere model (simplified)
        # P = P0 * exp(-altitude/scale_height)
        P0 = 760.0  # Sea level pressure in mmHg
        scale_height = 29921.0  # Scale height in feet
        
        return P0 * np.exp(-altitude/scale_height)
