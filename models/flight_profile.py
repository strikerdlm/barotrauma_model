"""
Flight profile class for barotrauma simulation
Defines the flight characteristics and ET dysfunction parameters
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

@dataclass(slots=True)
class FlightProfile:
    """
    Flight profile used by the legacy `models` simulation stack.

    Notes on backwards compatibility:
    - Historically this class was instantiated with
      (`cruise_altitude`, `ascent_rate`, `descent_rate`, `cruise_duration`, `et_dysfunction`).
    - Some validation/tests instantiate it with airport elevations instead, e.g.
      (`departure_elevation`, `destination_elevation`, `cruise_duration`).
      In that case we fall back to reasonable default climb/descent/cruise parameters.
    """

    # Primary, fully-specified profile inputs
    cruise_altitude: float = 35000.0
    ascent_rate: float = 2500.0
    descent_rate: float = 3000.0
    cruise_duration: float = 120.0
    et_dysfunction: float = 0.0

    # Optional airport elevations (feet). Used by some validation scripts/tests.
    departure_elevation: float = 0.0
    destination_elevation: float = 0.0

    def __init__(
        self,
        cruise_altitude: Optional[float] = None,
        ascent_rate: Optional[float] = None,
        descent_rate: Optional[float] = None,
        cruise_duration: float = 120.0,
        et_dysfunction: float = 0.0,
        departure_elevation: float = 0.0,
        destination_elevation: float = 0.0,
    ) -> None:
        # Allow "airport-elevation-only" construction (used in tests).
        if cruise_altitude is None:
            cruise_altitude = 35000.0
        if ascent_rate is None:
            ascent_rate = 2500.0
        if descent_rate is None:
            descent_rate = 3000.0

        # Validate parameters
        if not 0.0 <= et_dysfunction <= 1.0:
            raise ValueError("ET dysfunction must be between 0.0 and 1.0")
        if cruise_altitude <= 0:
            raise ValueError("Cruise altitude must be positive")
        if ascent_rate <= 0 or descent_rate <= 0:
            raise ValueError("Rates must be positive")
        if cruise_duration < 0:
            raise ValueError("Cruise duration must be non-negative")

        # Assign
        self.cruise_altitude = float(cruise_altitude)
        self.ascent_rate = float(ascent_rate)
        self.descent_rate = float(descent_rate)
        self.cruise_duration = float(cruise_duration)
        self.et_dysfunction = float(et_dysfunction)
        self.departure_elevation = float(departure_elevation)
        self.destination_elevation = float(destination_elevation)
    
    def get_altitude_at_time(self, time_min: float) -> Tuple[float, float]:
        """
        Calculate altitude and rate of change at given time
        
        Args:
            time_min: Time in minutes from takeoff
            
        Returns:
            Tuple of (altitude in feet, rate of change in feet/minute)
        """
        # Calculate phase transition times
        ascent_time = self.cruise_altitude / self.ascent_rate
        cruise_end_time = ascent_time + self.cruise_duration
        total_time = cruise_end_time + self.cruise_altitude / self.descent_rate
        
        # Determine flight phase and calculate altitude
        if time_min <= ascent_time:  # Climbing
            altitude = self.ascent_rate * time_min
            rate = self.ascent_rate
        elif time_min <= cruise_end_time:  # Cruise
            altitude = self.cruise_altitude
            rate = 0.0
        elif time_min <= total_time:  # Descending
            descent_time = time_min - cruise_end_time
            altitude = self.cruise_altitude - (self.descent_rate * descent_time)
            rate = -self.descent_rate
        else:  # Flight completed
            altitude = 0.0
            rate = 0.0
        
        return altitude, rate
    
    def altitude_to_pressure_mmHg(self, altitude_ft: float) -> float:
        """
        Convert altitude to pressure in mmHg using standard atmosphere model
        
        Args:
            altitude_ft: Altitude in feet
            
        Returns:
            Pressure in mmHg
        """
        # Standard atmosphere model (simplified)
        # P = P0 * exp(-altitude/scale_height)
        P0 = 760.0  # Sea level pressure in mmHg
        scale_height = 29921.0  # Scale height in feet
        
        return float(P0 * np.exp(-altitude_ft / scale_height))
