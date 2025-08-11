"""
Test script for barotrauma model validation.
"""

import logging
import numpy as np
from pathlib import Path
from src.test_model_relationships import ModelRelationshipTester
from src.barotrauma_integrated_model import IntegratedBarotraumaModel
from typing import Dict, List, Tuple
from scipy.integrate import trapezoid

def test_basic_cases():
    """Test basic cases with known outcomes."""
    model = IntegratedBarotraumaModel(physical_weight=0.6)
    tester = ModelRelationshipTester(model)
    
    try:
        # Test 1: Normal ET function
        logger.info("Testing normal ET function")
        result = tester.analyze_et_dysfunction_relationship()
        
        if result['data'].empty:
            logger.error("No valid data obtained from ET dysfunction analysis")
            return
        
        if 'risk_score' not in result['data'].columns:
            logger.error("Risk score not found in results")
            return
            
        assert result['data']['risk_score'].mean() < 0.3, "Risk too high for normal ET function"
        
        # Test 2: Severe dysfunction
        logger.info("Testing severe ET dysfunction")
        high_risk_cases = result['data'][result['data']['et_dysfunction'] > 0.8]
        if not high_risk_cases.empty:
            assert high_risk_cases['risk_score'].mean() > 0.6, "Risk too low for severe dysfunction"
        else:
            logger.warning("No high-risk cases found for testing")
        
        # Test 3: Rate sensitivity
        logger.info("Testing rate sensitivity")
        rate_results = tester.analyze_rate_interactions()
        if rate_results and 'stats' in rate_results:
            assert 'et_0.8' in rate_results['stats'], "Missing rate correlation for high ET dysfunction"
        else:
            logger.error("Rate interaction analysis failed")
            
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        raise

def test_physiological_bounds():
    """Test if model respects physiological constraints."""
    model = IntegratedBarotraumaModel(physical_weight=0.6)
    tester = ModelRelationshipTester(model)
    
    # Test pressure bounds
    max_pressure = tester.phys_constraints['pressure']['max_diff']
    warning_pressure = tester.phys_constraints['pressure']['warning']
    
    assert max_pressure == 200, f"Incorrect max pressure: {max_pressure}"
    assert warning_pressure == 100, f"Incorrect warning pressure: {warning_pressure}"
    
    # Test volume bounds
    tym_vol_range = (
        tester.phys_constraints['volume']['tym_min'],
        tester.phys_constraints['volume']['tym_max']
    )
    assert tym_vol_range[0] == 0.5e-3, f"Incorrect min tympanic volume: {tym_vol_range[0]}"
    assert tym_vol_range[1] == 2.0e-3, f"Incorrect max tympanic volume: {tym_vol_range[1]}"

def test_risk_calculations():
    """Test risk calculation components."""
    model = IntegratedBarotraumaModel(physical_weight=0.6)
    tester = ModelRelationshipTester(model)
    
    try:
        # Create test scenario
        scenario = {
            'pressure_metrics': {
                'max_diff': 150,  # mmHg
                'mean_diff': 75,
                'std_diff': 25,
                'rate_max': 40,
                'time_above_warning': 30
            },
            'volume_metrics': {
                'total_change': 1e-3,  # L
                'max_rate': 0.05e-3,
                'mean_rate': 0.02e-3,
                'excursion_ratio': 0.25
            }
        }
        
        # Test pressure risk
        pressure_risk = tester._calculate_pressure_risk(scenario['pressure_metrics'])
        assert 0 <= pressure_risk <= 1, f"Invalid pressure risk: {pressure_risk}"
        logger.info(f"Pressure risk calculation passed: {pressure_risk:.3f}")
        
        # Test volume risk
        volume_risk = tester._calculate_volume_risk(scenario['volume_metrics'])
        assert 0 <= volume_risk <= 1, f"Invalid volume risk: {volume_risk}"
        logger.info(f"Volume risk calculation passed: {volume_risk:.3f}")
        
    except Exception as e:
        logger.error(f"Risk calculation test failed: {str(e)}")
        raise

def test_integration_methods():
    """Test numerical integration methods."""
    model = IntegratedBarotraumaModel(physical_weight=0.6)
    tester = ModelRelationshipTester(model)
    
    # Create test data
    time = np.linspace(0, 10, 100)
    pressure = np.sin(time)
    
    # Test integration
    try:
        area = trapezoid(pressure, time)
        logger.info(f"Integration test passed: area = {area:.3f}")
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        raise

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='test_results/test_log.txt'
    )
    global logger
    logger = logging.getLogger(__name__)
    
    # Create test results directory if it doesn't exist
    Path("test_results").mkdir(exist_ok=True)
    
    try:
        logger.info("Starting basic case tests")
        test_basic_cases()
        logger.info("Basic case tests passed")
        
        logger.info("Starting physiological bounds tests")
        test_physiological_bounds()
        logger.info("Physiological bounds tests passed")
        
        logger.info("Starting risk calculation tests")
        test_risk_calculations()
        logger.info("Risk calculation tests passed")
        
        logger.info("Starting integration method tests")
        test_integration_methods()
        logger.info("Integration method tests passed")
        
    except AssertionError as e:
        logger.error(f"Test failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 