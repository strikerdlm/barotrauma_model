"""
Main script to validate and fix the barotrauma model.
"""

import logging
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

from fix_model import apply_model_fixes
from barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile
from barotrauma_integrated_model import IntegratedBarotraumaModel

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/main.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def generate_test_scenarios() -> List[Dict]:
    """Generate test scenarios covering different conditions."""
    scenarios = []
    
    # ET dysfunction levels
    dysfunction_levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    # Flight profiles
    flight_profiles = [
        {'initial_alt': 0, 'final_alt': 35000, 'climb_rate': 2000, 'descent_rate': 1500},
        {'initial_alt': 0, 'final_alt': 25000, 'climb_rate': 1500, 'descent_rate': 1000},
        {'initial_alt': 0, 'final_alt': 40000, 'climb_rate': 2500, 'descent_rate': 2000}
    ]
    
    # Generate combinations
    for dysfunction in dysfunction_levels:
        for profile in flight_profiles:
            scenario = {
                'et_dysfunction': dysfunction,
                'V_tym': 1.0e-3,
                'V_mas': 7.75e-3,
                'k_MEM': {
                    'O2': 0.015,
                    'CO2': 0.025,
                    'N2': 0.0008,
                    'H2O': 0.035
                },
                'flight_profile': profile
            }
            scenarios.append(scenario)
    
    return scenarios

def run_scenario(scenario: Dict, solver_params: Dict = None) -> Dict:
    """Run a single scenario and return results."""
    try:
        # Extract flight profile
        profile = scenario.pop('flight_profile')
        
        # Create simulation
        sim = BarotraumaSimulation(scenario)
        if solver_params:
            sim.solver_params = solver_params
        
        # Generate flight profile
        time_array, _, _, P_cabin_func, altitude_func = simulate_flight_profile(
            profile['initial_alt'],
            profile['final_alt'],
            profile['climb_rate'],
            profile['descent_rate'],
            120  # Fixed cruise duration
        )
        
        # Run simulation
        result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
        
        if result is None:
            return {'status': 'failed', 'error': 'Simulation returned None'}
            
        time, P_ME, V_ME, delta_P, risk, risk_score = result
        
        return {
            'status': 'success',
            'time': time.tolist(),
            'P_ME': P_ME.tolist(),
            'V_ME': V_ME.tolist(),
            'delta_P': delta_P,
            'risk': risk,
            'risk_score': risk_score
        }
        
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def analyze_results(results: List[Dict]) -> Dict:
    """Analyze simulation results across scenarios."""
    analysis = {
        'success_rate': 0,
        'avg_risk_score': 0,
        'risk_by_dysfunction': {},
        'stability_issues': 0
    }
    
    successful_runs = [r for r in results if r['status'] == 'success']
    analysis['success_rate'] = len(successful_runs) / len(results)
    
    if successful_runs:
        risk_scores = [r['risk_score'] for r in successful_runs]
        analysis['avg_risk_score'] = np.mean(risk_scores)
        
        # Analyze stability
        for run in successful_runs:
            if np.any(np.abs(np.array(run['P_ME'])) > 200) or \
               np.any(np.array(run['V_ME']) <= 0):
                analysis['stability_issues'] += 1
    
    return analysis

def main():
    """Main function to validate and fix the model."""
    logger = setup_logging()
    logger.info("Starting model validation and fixes")
    
    try:
        # Create necessary directories
        for dir_name in ['logs', 'results', 'figures']:
            Path(dir_name).mkdir(exist_ok=True)
        
        # Step 1: Generate test scenarios
        logger.info("Generating test scenarios")
        scenarios = generate_test_scenarios()
        
        # Step 2: Run initial tests
        logger.info("Running initial tests")
        initial_results = []
        for scenario in scenarios:
            result = run_scenario(scenario.copy())
            initial_results.append(result)
        
        # Step 3: Analyze initial results
        logger.info("Analyzing initial results")
        initial_analysis = analyze_results(initial_results)
        
        # Step 4: Apply fixes if needed
        if initial_analysis['success_rate'] < 0.9 or initial_analysis['stability_issues'] > 0:
            logger.info("Applying model fixes")
            fixed_params, solver_params = apply_model_fixes(scenarios[0])
            
            # Run tests with fixed parameters
            fixed_results = []
            for scenario in scenarios:
                # Update scenario with fixed parameters
                fixed_scenario = scenario.copy()
                fixed_scenario.update(fixed_params)
                result = run_scenario(fixed_scenario, solver_params)
                fixed_results.append(result)
            
            # Analyze fixed results
            fixed_analysis = analyze_results(fixed_results)
            
            # Save comparison
            comparison = {
                'initial_analysis': initial_analysis,
                'fixed_analysis': fixed_analysis
            }
            
            with open('results/model_comparison.json', 'w') as f:
                json.dump(comparison, f, indent=4)
            
            # Plot comparison
            plt.figure(figsize=(12, 6))
            metrics = ['success_rate', 'avg_risk_score', 'stability_issues']
            x = np.arange(len(metrics))
            width = 0.35
            
            plt.bar(x - width/2, [initial_analysis[m] for m in metrics], width, label='Initial')
            plt.bar(x + width/2, [fixed_analysis[m] for m in metrics], width, label='Fixed')
            
            plt.xlabel('Metrics')
            plt.ylabel('Value')
            plt.title('Model Performance Comparison')
            plt.xticks(x, metrics)
            plt.legend()
            
            plt.savefig('figures/model_comparison.png')
            plt.close()
            
            logger.info("Model fixes completed and results saved")
        else:
            logger.info("Model performing well, no fixes needed")
        
        return True
        
    except Exception as e:
        logger.error(f"Main execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    main() 