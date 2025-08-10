"""
Quick statistical analysis of barotrauma risk factors.
Focused analysis with specific parameter combinations for rapid descent scenarios.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
import sys
from os.path import dirname, abspath
import logging
import json

# Add parent directory to Python path
parent_dir = dirname(dirname(abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile

def setup_logging():
    """Setup logging configuration."""
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/quick_analysis.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def run_focused_analysis():
    """Run focused analysis with rapid descent scenarios."""
    logger = logging.getLogger(__name__)
    results = []
    
    # Key parameter values
    et_dysfunctions = [0.0, 0.25, 0.5, 0.75, 1.0]  # Five levels of dysfunction
    descent_rates = [2000, 4000, 6000, 8000]  # Four descent rates (ft/min)
    cruise_altitude = 25000  # Fixed cruise altitude (ft)
    cruise_duration = 10  # Fixed cruise duration (min)
    
    total_combinations = len(et_dysfunctions) * len(descent_rates)
    logger.info(f"Running {total_combinations} combinations...")
    
    for et_dys in et_dysfunctions:
        for desc_rate in descent_rates:
            try:
                # Create simulation parameters
                params = {
                    'et_dysfunction': et_dys,
                    'V_tym': 1.0e-3,
                    'V_mas': 7.75e-3
                }
                
                # Create simulation
                sim = BarotraumaSimulation(params)
                
                # Generate flight profile
                time_array, _, _, p_func, alt_func = simulate_flight_profile(
                    initial_altitude_ft=0,
                    final_altitude_ft=cruise_altitude,
                    climb_rate_ft_min=2000,  # Fixed climb rate
                    descent_rate_ft_min=desc_rate,
                    cruise_duration_min=cruise_duration
                )
                
                # Run simulation
                result = sim.simulate_flight(time_array, p_func, alt_func)
                
                if result is not None:
                    _, P_ME, V_ME, delta_P, risk_cat, risk_score = result
                    
                    # Calculate metrics
                    max_pressure_diff = np.max(np.abs(delta_P))
                    mean_pressure_diff = np.mean(np.abs(delta_P))
                    volume_change = np.max(V_ME) - np.min(V_ME)
                    
                    # Calculate descent time
                    descent_time = cruise_altitude / desc_rate  # minutes
                    
                    results.append({
                        'et_dysfunction': et_dys,
                        'descent_rate': desc_rate,
                        'descent_time': descent_time,
                        'risk_score': risk_score,
                        'risk_category': risk_cat,
                        'max_pressure_diff': max_pressure_diff,
                        'mean_pressure_diff': mean_pressure_diff,
                        'volume_change': volume_change
                    })
                    
                    logger.info(f"Completed simulation for ET dysfunction {et_dys}, descent rate {desc_rate}")
            
            except Exception as e:
                logger.error(f"Error in simulation: {str(e)}")
                continue
    
    return pd.DataFrame(results)

def analyze_and_plot(df: pd.DataFrame):
    """Analyze results and generate key plots."""
    logger = logging.getLogger(__name__)
    
    # Create output directories
    for dir_name in ['results', 'figures']:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Basic statistics
    stats_dict = {
        'risk_score': df['risk_score'].describe().to_dict(),
        'max_pressure_diff': df['max_pressure_diff'].describe().to_dict(),
        'mean_pressure_diff': df['mean_pressure_diff'].describe().to_dict(),
        'volume_change': df['volume_change'].describe().to_dict()
    }
    
    # Save statistics
    with open('results/quick_stats.json', 'w') as f:
        json.dump(stats_dict, f, indent=4)
    
    # Save raw data
    df.to_csv('results/quick_results.csv', index=False)
    
    # Generate plots
    plt.rcParams['figure.figsize'] = [12, 6]
    plt.rcParams['axes.grid'] = True
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    
    # 1. ET Dysfunction vs Risk Score by Descent Rate
    plt.figure()
    for rate in sorted(df['descent_rate'].unique()):
        subset = df[df['descent_rate'] == rate]
        plt.plot(subset['et_dysfunction'], subset['risk_score'], 
                marker='o', label=f'{rate} ft/min')
    
    plt.title('Risk Score vs ET Dysfunction by Descent Rate', fontsize=14)
    plt.xlabel('ET Dysfunction Level')
    plt.ylabel('Risk Score')
    plt.legend(title='Descent Rate')
    plt.savefig('figures/risk_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Risk Score vs Descent Rate by ET Dysfunction
    plt.figure()
    for et_dys in sorted(df['et_dysfunction'].unique()):
        subset = df[df['et_dysfunction'] == et_dys]
        plt.plot(subset['descent_rate'], subset['risk_score'], 
                marker='o', label=f'ET Dys {et_dys:.2f}')
    
    plt.title('Risk Score vs Descent Rate by ET Dysfunction', fontsize=14)
    plt.xlabel('Descent Rate (ft/min)')
    plt.ylabel('Risk Score')
    plt.legend(title='ET Dysfunction')
    plt.savefig('figures/descent_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Pressure Difference Analysis
    plt.figure()
    scatter = plt.scatter(df['descent_rate'], df['max_pressure_diff'],
                         c=df['et_dysfunction'], s=df['risk_score']*200,
                         cmap='viridis', alpha=0.6)
    plt.colorbar(scatter, label='ET Dysfunction')
    
    plt.title('Maximum Pressure Difference vs Descent Rate', fontsize=14)
    plt.xlabel('Descent Rate (ft/min)')
    plt.ylabel('Maximum Pressure Difference (mmHg)')
    plt.savefig('figures/pressure_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Print key findings
    logger.info("\nKey Findings:")
    logger.info(f"Number of simulations: {len(df)}")
    logger.info(f"Overall mean risk score: {df['risk_score'].mean():.3f}")
    
    logger.info("\nRisk scores by ET dysfunction level:")
    for et_dys in sorted(df['et_dysfunction'].unique()):
        subset = df[df['et_dysfunction'] == et_dys]
        mean_risk = subset['risk_score'].mean()
        std_risk = subset['risk_score'].std()
        logger.info(f"ET dysfunction {et_dys:.2f}: {mean_risk:.3f} ± {std_risk:.3f}")
    
    logger.info("\nRisk scores by descent rate:")
    for rate in sorted(df['descent_rate'].unique()):
        subset = df[df['descent_rate'] == rate]
        mean_risk = subset['risk_score'].mean()
        std_risk = subset['risk_score'].std()
        logger.info(f"Descent rate {rate} ft/min: {mean_risk:.3f} ± {std_risk:.3f}")
    
    # Statistical tests
    # 1. Effect of ET dysfunction
    f_stat, p_val = stats.f_oneway(*[group['risk_score'].values 
                                    for name, group in df.groupby('et_dysfunction')])
    logger.info(f"\nET dysfunction effect: F={f_stat:.2f}, p={p_val:.4f}")
    
    # 2. Effect of descent rate
    f_stat, p_val = stats.f_oneway(*[group['risk_score'].values 
                                    for name, group in df.groupby('descent_rate')])
    logger.info(f"Descent rate effect: F={f_stat:.2f}, p={p_val:.4f}")
    
    # 3. Correlation analysis
    correlations = df[['et_dysfunction', 'descent_rate', 'descent_time', 
                      'risk_score', 'max_pressure_diff']].corr()
    logger.info("\nCorrelations with risk score:")
    for var in correlations.index:
        if var != 'risk_score':
            corr = correlations.loc[var, 'risk_score']
            logger.info(f"{var}: {corr:.3f}")

def main():
    """Run quick statistical analysis."""
    logger = setup_logging()
    logger.info("Starting quick statistical analysis")
    
    try:
        # Run analysis
        df = run_focused_analysis()
        
        # Analyze and plot results
        analyze_and_plot(df)
        
        logger.info("Analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 