"""
Validation module for barotrauma simulation model.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from src.barotrauma_simulation import BarotraumaSimulation, simulate_flight_profile
import seaborn as sns
from sklearn.metrics import r2_score
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class BarotraumaValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Standard flight profile for testing
        self.standard_profile = {
            'initial_altitude_ft': 0,
            'final_altitude_ft': 35000,
            'climb_rate_ft_min': 2000,
            'descent_rate_ft_min': 2000,
            'cruise_duration_min': 30
        }
    
    def run_et_dysfunction_analysis(self, n_samples=50):
        """
        Analyze the relationship between ET dysfunction and barotrauma risk.
        """
        # Generate ET dysfunction values (more samples in higher range)
        et_values = np.concatenate([
            np.linspace(0, 0.5, n_samples//2),  # More samples in lower range
            np.linspace(0.5, 1.0, n_samples//2)  # More samples in higher range
        ])
        
        results = []
        for et_dysfunction in et_values:
            # Create scenario with varying ET dysfunction
            scenario = {
                **self.standard_profile,
                'et_dysfunction': et_dysfunction,
                'inflammation': 0.2  # Fixed moderate inflammation
            }
            
            # Run simulation
            sim = BarotraumaSimulation(scenario)
            time_array, altitude_array, cabin_pressure_points, P_cabin_func, altitude_func = \
                simulate_flight_profile(**self.standard_profile)
            
            result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
            
            if result is not None:
                _, P_ME_history, V_ME_history, delta_P, risk, risk_score = result
                
                # Calculate additional metrics
                max_pressure_diff = np.max(np.abs(delta_P))
                mean_pressure_diff = np.mean(np.abs(delta_P))
                pressure_diff_std = np.std(delta_P)
                volume_change = np.max(V_ME_history) - np.min(V_ME_history)
                
                results.append({
                    'et_dysfunction': et_dysfunction,
                    'risk_score': risk_score,
                    'max_pressure_diff': max_pressure_diff,
                    'mean_pressure_diff': mean_pressure_diff,
                    'pressure_diff_std': pressure_diff_std,
                    'volume_change': volume_change,
                    'risk_category': risk
                })
        
        df = pd.DataFrame(results)
        
        # Add ET dysfunction quartile information
        df['et_dysfunction_binned'] = pd.qcut(df['et_dysfunction'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
        
        return df
    
    def analyze_results(self, df):
        """
        Perform statistical analysis on the results.
        """
        # Calculate correlations
        correlations = df[['et_dysfunction', 'risk_score', 'max_pressure_diff', 
                          'mean_pressure_diff', 'volume_change']].corr()
        
        # Perform regression analysis
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            df['et_dysfunction'], df['risk_score']
        )
        
        r2 = r2_score(df['et_dysfunction'], df['risk_score'])
        
        # Calculate risk statistics by quartile
        quartile_stats = df.groupby('et_dysfunction_binned').agg({
            'risk_score': ['mean', 'std'],
            'max_pressure_diff': ['mean', 'std']
        })
        
        # Calculate risk category proportions
        risk_proportions = df['risk_category'].value_counts(normalize=True)
        
        return {
            'correlations': correlations,
            'regression': {
                'slope': slope,
                'intercept': intercept,
                'r_value': r_value,
                'p_value': p_value,
                'std_err': std_err,
                'r2': r2
            },
            'quartile_stats': quartile_stats,
            'risk_proportions': risk_proportions
        }
    
    def plot_results(self, df, stats_results):
        """
        Create visualization of the results.
        """
        plt.figure(figsize=(15, 12))
        
        # Plot 1: ET Dysfunction vs Risk Score with quartile boxes
        plt.subplot(2, 2, 1)
        sns.boxplot(data=df, x='et_dysfunction_binned', y='risk_score', color='lightgray')
        sns.scatterplot(data=df, x='et_dysfunction', y='risk_score', hue='risk_category', alpha=0.6)
        plt.title('ET Dysfunction vs Risk Score')
        plt.xlabel('ET Dysfunction Quartile')
        plt.ylabel('Risk Score')
        
        # Plot 2: ET Dysfunction vs Pressure Differences
        plt.subplot(2, 2, 2)
        sns.scatterplot(data=df, x='et_dysfunction', y='max_pressure_diff', hue='risk_category')
        plt.title('ET Dysfunction vs Max Pressure Difference')
        plt.xlabel('ET Dysfunction')
        plt.ylabel('Max Pressure Difference (mmHg)')
        
        # Plot 3: Risk Distribution
        plt.subplot(2, 2, 3)
        stats_results['risk_proportions'].plot(kind='bar')
        plt.title('Distribution of Risk Categories')
        plt.xlabel('Risk Category')
        plt.ylabel('Proportion')
        
        # Plot 4: Correlation Heatmap
        plt.subplot(2, 2, 4)
        sns.heatmap(stats_results['correlations'], annot=True, cmap='coolwarm', center=0)
        plt.title('Correlation Matrix')
        
        plt.tight_layout()
        plt.show()
        
        # Print statistical summary
        self.logger.info("\nStatistical Summary:")
        self.logger.info(f"Regression slope: {stats_results['regression']['slope']:.3f}")
        self.logger.info(f"R-squared: {stats_results['regression']['r2']:.3f}")
        self.logger.info(f"P-value: {stats_results['regression']['p_value']:.3e}")
    
    def validate_physiological_assumptions(self, df):
        """
        Validate that the model follows expected physiological patterns.
        """
        self.logger.info("\nValidating Physiological Assumptions:")
        
        # 1. Analyze risk progression by ET dysfunction quartile
        risk_by_quartile = df.groupby('et_dysfunction_binned')['risk_score'].mean()
        
        self.logger.info("\n1. Risk progression by ET dysfunction quartile:")
        for quartile in ['Q1', 'Q2', 'Q3', 'Q4']:
            self.logger.info(f"   {quartile}: {risk_by_quartile[quartile]:.2f}")
        
        # 2. Check if risk increases between quartiles
        risk_increases = np.all(np.diff(risk_by_quartile) > 0)
        self.logger.info(f"\n2. Risk increases between quartiles: {risk_increases}")
        
        # 3. Analyze risk distribution
        risk_dist = df['risk_category'].value_counts(normalize=True)
        self.logger.info("\n3. Risk distribution:")
        for category, proportion in risk_dist.items():
            self.logger.info(f"   {category}: {proportion*100:.1f}%")
        
        # 4. Validate pressure-dysfunction relationship
        pressure_corr = df['et_dysfunction'].corr(df['max_pressure_diff'])
        self.logger.info(f"\n4. Pressure-dysfunction correlation: {pressure_corr:.3f}")
        
        # 5. Check physiological limits
        self.logger.info("\n5. Physiological limits check:")
        self.logger.info(f"   Max pressure difference: {df['max_pressure_diff'].max():.1f} mmHg")
        self.logger.info(f"   Max volume change: {df['volume_change'].max()*1000:.2f} mL")
        
        return {
            'risk_progression': risk_increases,
            'pressure_correlation': pressure_corr,
            'max_pressure': df['max_pressure_diff'].max(),
            'max_volume_change': df['volume_change'].max()
        }
    
    def validate_model(self):
        """
        Run complete validation of the model.
        """
        self.logger.info("Running ET dysfunction analysis...")
        results_df = self.run_et_dysfunction_analysis()
        
        self.logger.info("Analyzing results...")
        stats_results = self.analyze_results(results_df)
        
        self.logger.info("Plotting results...")
        self.plot_results(results_df, stats_results)
        
        # Validate physiological assumptions
        validation_results = self.validate_physiological_assumptions(results_df)
        
        return results_df, stats_results, validation_results

def main():
    setup_logging()
    validator = BarotraumaValidator()
    validator.validate_model()

if __name__ == "__main__":
    main() 