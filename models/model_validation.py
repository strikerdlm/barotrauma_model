"""
Validation script for barotrauma simulation
Tests different flight profiles and ET dysfunction levels
"""

import numpy as np
from barotrauma_simulation import FlightProfile, BarotraumaSimulation

def validate_pressure_ranges(results):
    """Validate that pressures stay within physiological ranges (all in mmHg)"""
    # Convert typical unpressurized aircraft altitudes to pressure
    min_pressure = 282.0  # mmHg (approximately 25,000 ft)
    max_pressure = 760.0  # mmHg (sea level)
    
    # Validate cabin pressure ranges
    assert np.all(results['P_cabin'] >= min_pressure), f"Cabin pressure below {min_pressure} mmHg"
    assert np.all(results['P_cabin'] <= max_pressure), f"Cabin pressure exceeds {max_pressure} mmHg"
    
    # Middle ear pressure should stay within physiological limits
    assert np.all(results['P_ME'] >= 0), "Middle ear pressure went negative"
    assert np.all(results['P_ME'] <= max_pressure), f"Middle ear pressure exceeds {max_pressure} mmHg"

def validate_physiological_constraints(results, et_dysfunction: float):
    """Validate that the results follow physiological constraints"""
    # Calculate actual altitude change rates
    altitude_rates = np.abs(results['altitude_rate'])
    max_rate = np.max(altitude_rates)
    
    if et_dysfunction > 0.5:
        # Check if pressure changes are within limits for significant ET dysfunction
        assert max_rate <= 2000, f"Altitude change rate ({max_rate:.0f} ft/min) exceeded limit for ET dysfunction {et_dysfunction:.1f}"
        
        # Check for increased barotrauma risk
        assert np.mean(results['barotitis']) > 0.1, f"Expected higher barotitis risk for ET dysfunction {et_dysfunction:.1f}"
    else:
        # Normal to mild dysfunction should handle higher rates
        assert max_rate <= 18000, f"Altitude change rate ({max_rate:.0f} ft/min) exceeded maximum limit"
    
    # Verify ET collapse behavior
    if et_dysfunction > 0.5:
        assert np.any(results['ET_collapsed']), f"No ET collapse detected for ET dysfunction {et_dysfunction:.1f}"
    else:
        assert not np.any(results['ET_collapsed']), "Unexpected ET collapse for normal ET function"

def run_validation():
    """Run validation tests on different flight profiles"""
    # Test scenarios
    test_scenarios = [
        {
            'name': "Normal ET - Moderate Climb",
            'profile': FlightProfile(
                cruise_altitude=25000.0,  # feet
                ascent_rate=1500.0,      # feet/min
                descent_rate=2000.0,      # feet/min
                cruise_duration=60.0,     # minutes
                et_dysfunction=0.0        # normal function
            )
        },
        {
            'name': "Normal ET - Rapid Climb",
            'profile': FlightProfile(
                cruise_altitude=25000.0,
                ascent_rate=2500.0,
                descent_rate=3000.0,
                cruise_duration=60.0,
                et_dysfunction=0.0
            )
        },
        {
            'name': "Moderate ET Dysfunction",
            'profile': FlightProfile(
                cruise_altitude=25000.0,
                ascent_rate=1500.0,
                descent_rate=1500.0,
                cruise_duration=60.0,
                et_dysfunction=0.6
            )
        },
        {
            'name': "Severe ET Dysfunction",
            'profile': FlightProfile(
                cruise_altitude=25000.0,
                ascent_rate=1000.0,
                descent_rate=1000.0,
                cruise_duration=60.0,
                et_dysfunction=0.9
            )
        }
    ]
    
    for scenario in test_scenarios:
        try:
            print(f"\nTesting scenario: {scenario['name']}")
            
            # Initialize simulation
            sim = BarotraumaSimulation(scenario['profile'])
            
            # Run simulation
            results = sim.run_simulation()
            
            # Validate results
            validate_pressure_ranges(results)
            validate_physiological_constraints(results, scenario['profile'].et_dysfunction)
            
            # Analyze results
            analysis = sim.analyze_results(results)
            
            # Print detailed results
            print("\nFlight Profile:")
            print(f"Cruise altitude: {scenario['profile'].cruise_altitude:.0f} feet")
            print(f"Ascent rate: {scenario['profile'].ascent_rate:.0f} ft/min")
            print(f"Descent rate: {scenario['profile'].descent_rate:.0f} ft/min")
            print(f"ET dysfunction: {scenario['profile'].et_dysfunction:.1f}")
            
            print("\nRisk Analysis:")
            print(f"Maximum pressure differential: {analysis['max_pressure_differential']:.1f} mmHg")
            print(f"Barotitis risk: {analysis['barotitis_risk']:.1f}%")
            print(f"Baromyringitis risk: {analysis['baromyringitis_risk']:.1f}%")
            print(f"ET locked duration: {analysis['et_locked_duration']:.1f}%")
            print(f"ET collapse duration: {analysis['et_collapse_duration']:.1f}%")
            print(f"Overall risk: {analysis['overall_risk']:.1f}%")
            
            print(f"\n✓ {scenario['name']} - All tests passed")
            
        except Exception as e:
            print(f"\n✗ {scenario['name']} - Test failed: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        run_validation()
        print("\nAll validation tests passed successfully!")
    except Exception as e:
        print(f"\nValidation failed during scenario testing")
        exit(1) 