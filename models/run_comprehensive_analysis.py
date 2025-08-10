"""
Comprehensive analysis of barotrauma risk using integrated model
"""

from integrated_model import IntegratedModel, SimulationConfig
from statistical_analysis import calculate_confidence_interval
from flight_profile import FlightProfile
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List

def run_comprehensive_analysis():
    # Test parameters based on physiological data
    et_dysfunctions = [0.0, 0.3, 0.6, 0.9]  # none, mild, moderate, severe
    descent_rates = [1000, 2000, 4000, 8000, 12000, 18000]  # ft/min
    ascent_rates = [1000, 2000, 3000]  # ft/min
    cruise_altitude = 25000  # ft
    cruise_duration = 30  # minutes
    
    results_list = []
    
    print("Running comprehensive analysis...")
    
    # Run simulations for all combinations
    for dysfunction in et_dysfunctions:
        for descent_rate in descent_rates:
            for ascent_rate in ascent_rates:
                print(f"Testing: ET dysfunction={dysfunction:.1f}, "
                      f"descent={descent_rate} ft/min, ascent={ascent_rate} ft/min")
                
                # Create flight profile
                profile = FlightProfile(
                    ascent_rate=ascent_rate,
                    descent_rate=descent_rate,
                    cruise_altitude=cruise_altitude,
                    cruise_duration=cruise_duration,
                    et_dysfunction=dysfunction
                )
                
                # Run multiple iterations for statistical analysis
                n_iterations = 5
                iteration_results = []
                
                for _ in range(n_iterations):
                    sim = BarotraumaSimulation(profile)
                    sim_results = sim.run_simulation(dt=1.0)
                    
                    # Calculate metrics
                    max_dp = np.max(np.abs(sim_results['dP']))
                    et_locked_duration = np.mean(sim_results['ET_locked'])
                    barotitis_duration = np.mean(sim_results['barotitis'])
                    baromyringitis_duration = np.mean(sim_results['baromyringitis'])
                    
                    iteration_results.append({
                        'max_pressure_differential': max_dp,
                        'et_locked_duration': et_locked_duration,
                        'barotitis_risk': barotitis_duration,
                        'baromyringitis_risk': baromyringitis_duration
                    })
                
                # Calculate mean results
                mean_results = {k: np.mean([r[k] for r in iteration_results]) 
                              for k in iteration_results[0].keys()}
                
                # Add to results list
                results_list.append({
                    'et_dysfunction': dysfunction,
                    'descent_rate': descent_rate,
                    'ascent_rate': ascent_rate,
                    **mean_results
                })
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results_list)
    
    # Statistical analysis
    print("\nCalculating statistics...")
    
    # Group by ET dysfunction
    dysfunction_stats = results_df.groupby('et_dysfunction').agg({
        'max_pressure_differential': ['mean', 'std'],
        'barotitis_risk': ['mean', 'std'],
        'baromyringitis_risk': ['mean', 'std'],
        'et_locked_duration': ['mean', 'std']
    })
    
    # Calculate confidence intervals
    for dysfunction in et_dysfunctions:
        subset = results_df[results_df['et_dysfunction'] == dysfunction]
        for metric in ['max_pressure_differential', 'barotitis_risk', 
                      'baromyringitis_risk', 'et_locked_duration']:
            ci_upper, ci_lower = calculate_confidence_interval(
                subset[metric].values, 
                len(subset)
            )
            dysfunction_stats.loc[dysfunction, (metric, 'ci_upper')] = ci_upper
            dysfunction_stats.loc[dysfunction, (metric, 'ci_lower')] = ci_lower
    
    # Generate visualizations
    print("\nGenerating plots...")
    
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Risk vs ET Dysfunction
    plt.subplot(2, 2, 1)
    for rate in [1000, 8000, 18000]:
        subset = results_df[results_df['descent_rate'] == rate]
        plt.plot(subset['et_dysfunction'], subset['barotitis_risk'] * 100, 
                'o-', label=f'Descent {rate} ft/min')
    plt.xlabel('ET Dysfunction Level')
    plt.ylabel('Barotitis Risk (%)')
    plt.title('Barotitis Risk vs ET Dysfunction')
    plt.legend()
    plt.grid(True)
    
    # Plot 2: Pressure Differential vs Descent Rate
    plt.subplot(2, 2, 2)
    for dysfunction in et_dysfunctions:
        subset = results_df[results_df['et_dysfunction'] == dysfunction]
        plt.plot(subset['descent_rate'], subset['max_pressure_differential'],
                'o-', label=f'ET dysfunction {dysfunction:.1f}')
    plt.xlabel('Descent Rate (ft/min)')
    plt.ylabel('Max Pressure Differential (mmHg)')
    plt.title('Pressure vs Descent Rate')
    plt.legend()
    plt.grid(True)
    
    # Plot 3: ET Locked Duration
    plt.subplot(2, 2, 3)
    for dysfunction in et_dysfunctions:
        subset = results_df[results_df['et_dysfunction'] == dysfunction]
        plt.plot(subset['descent_rate'], subset['et_locked_duration'] * 100,
                'o-', label=f'ET dysfunction {dysfunction:.1f}')
    plt.xlabel('Descent Rate (ft/min)')
    plt.ylabel('ET Locked Duration (%)')
    plt.title('ET Locked Duration vs Descent Rate')
    plt.legend()
    plt.grid(True)
    
    # Plot 4: Risk Distribution
    plt.subplot(2, 2, 4)
    data = [results_df[results_df['et_dysfunction'] == d]['barotitis_risk'] * 100 
            for d in et_dysfunctions]
    plt.boxplot(data, labels=[f'{d:.1f}' for d in et_dysfunctions])
    plt.xlabel('ET Dysfunction Level')
    plt.ylabel('Barotitis Risk (%)')
    plt.title('Risk Distribution by ET Dysfunction')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('comprehensive_analysis.png', dpi=300, bbox_inches='tight')
    
    # Save results
    results_df.to_csv('comprehensive_results.csv', index=False)
    
    print("\nAnalysis complete!")
    print("Results saved to 'comprehensive_results.csv'")
    print("Plots saved to 'comprehensive_analysis.png'")
    
    return results_df, dysfunction_stats

if __name__ == "__main__":
    from barotrauma_simulation import BarotraumaSimulation
    results_df, stats = run_comprehensive_analysis()
    
    # Print summary statistics
    print("\nSummary Statistics by ET Dysfunction Level:")
    print(stats) 