"""
Comprehensive simulation analysis for barotrauma risk
Tests different combinations of ascent rates, descent rates, and ET dysfunction levels
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from barotrauma_simulation import BarotraumaSimulation
from flight_profile import FlightProfile

class SimulationAnalysis:
    """Advanced analysis of barotrauma simulation results with physiological parameters"""
    
    def __init__(self):
        # Physiological thresholds (mmHg)
        self.PASSIVE_OPENING_THRESHOLD = 15.0  # 2 kPa
        self.ET_LOCK_THRESHOLD = 90.0  # 12 kPa
        self.MEMBRANE_RUPTURE_THRESHOLD = 100.0
        
        # Time-based parameters
        self.ET_OPENING_DURATION_RANGE = (0.2, 0.7)  # seconds
        self.PRESSURE_EQUALIZATION_RATE = 43.2  # mmHg/s
        
        # Statistical analysis parameters
        self.CONFIDENCE_LEVEL = 0.95
        self.BOOTSTRAP_SAMPLES = 1000
    
    def run_batch_simulation(self, 
                           ascent_rates: List[float],
                           descent_rates: List[float],
                           cruise_altitudes: List[float],
                           et_dysfunctions: List[float],
                           n_iterations: int = 10) -> pd.DataFrame:
        """Run multiple simulations with different parameters"""
        results = []
        
        for ascent in ascent_rates:
            for descent in descent_rates:
                for altitude in cruise_altitudes:
                    for dysfunction in et_dysfunctions:
                        for _ in range(n_iterations):
                            profile = FlightProfile(
                                ascent_rate=ascent,
                                descent_rate=descent,
                                cruise_altitude=altitude,
                                cruise_duration=30,
                                et_dysfunction=dysfunction
                            )
                            sim = BarotraumaSimulation(profile)
                            sim_results = sim.run_simulation(dt=1.0)
                            analysis = self.analyze_single_simulation(sim_results, profile)
                            
                            results.append({
                                'ascent_rate': ascent,
                                'descent_rate': descent,
                                'cruise_altitude': altitude,
                                'et_dysfunction': dysfunction,
                                **analysis
                            })
        
        return pd.DataFrame(results)
    
    def analyze_single_simulation(self, results: Dict[str, np.ndarray], 
                                profile: FlightProfile) -> Dict[str, float]:
        """Analyze a single simulation with physiological metrics"""
        
        # Basic pressure metrics
        max_dp = np.max(np.abs(results['dP']))
        mean_dp = np.mean(np.abs(results['dP']))
        std_dp = np.std(results['dP'])
        
        # Time-based analysis
        total_time = len(results['time'])
        et_locked_duration = np.sum(results['ET_locked']) / total_time
        barotitis_duration = np.sum(results['barotitis']) / total_time
        baromyringitis_duration = np.sum(results['baromyringitis']) / total_time
        
        # Pressure threshold analysis
        time_above_passive = np.sum(np.abs(results['dP']) > self.PASSIVE_OPENING_THRESHOLD) / total_time
        time_above_lock = np.sum(np.abs(results['dP']) > self.ET_LOCK_THRESHOLD) / total_time
        time_above_rupture = np.sum(np.abs(results['dP']) > self.MEMBRANE_RUPTURE_THRESHOLD) / total_time
        
        # Phase-specific analysis
        ascent_mask = results['altitude_rate'] > 0
        descent_mask = results['altitude_rate'] < 0
        cruise_mask = results['altitude_rate'] == 0
        
        phase_analysis = {
            'ascent_max_dp': np.max(np.abs(results['dP'][ascent_mask])) if np.any(ascent_mask) else 0,
            'descent_max_dp': np.max(np.abs(results['dP'][descent_mask])) if np.any(descent_mask) else 0,
            'cruise_max_dp': np.max(np.abs(results['dP'][cruise_mask])) if np.any(cruise_mask) else 0
        }
        
        # Risk calculation with physiological weighting
        dysfunction = profile.et_dysfunction
        
        # Base risk factors
        pressure_risk = self._calculate_pressure_risk(max_dp)
        duration_risk = self._calculate_duration_risk(et_locked_duration)
        phase_risk = self._calculate_phase_risk(phase_analysis)
        
        # Dysfunction-weighted risk
        dysfunction_factor = self._calculate_dysfunction_factor(dysfunction)
        
        # Combined risk score with confidence interval
        risk_components = [
            pressure_risk * 0.4,
            duration_risk * 0.3,
            phase_risk * 0.3
        ]
        base_risk = np.sum(risk_components) * dysfunction_factor
        
        # Calculate confidence interval using bootstrap
        ci_lower, ci_upper = self._calculate_risk_confidence_interval(
            results['dP'], dysfunction_factor
        )
        
        return {
            'max_pressure_differential': max_dp,
            'mean_pressure_differential': mean_dp,
            'pressure_std': std_dp,
            'et_locked_duration': et_locked_duration * 100,
            'barotitis_duration': barotitis_duration * 100,
            'baromyringitis_duration': baromyringitis_duration * 100,
            'time_above_passive_threshold': time_above_passive * 100,
            'time_above_lock_threshold': time_above_lock * 100,
            'time_above_rupture_threshold': time_above_rupture * 100,
            'ascent_max_dp': phase_analysis['ascent_max_dp'],
            'descent_max_dp': phase_analysis['descent_max_dp'],
            'cruise_max_dp': phase_analysis['cruise_max_dp'],
            'risk_score': base_risk,
            'risk_ci_lower': ci_lower,
            'risk_ci_upper': ci_upper
        }
    
    def _calculate_pressure_risk(self, max_dp: float) -> float:
        """Calculate pressure-based risk with physiological thresholds"""
        if max_dp <= self.PASSIVE_OPENING_THRESHOLD:
            return 0.0
        elif max_dp <= self.ET_LOCK_THRESHOLD:
            return (max_dp - self.PASSIVE_OPENING_THRESHOLD) / (self.ET_LOCK_THRESHOLD - self.PASSIVE_OPENING_THRESHOLD)
        else:
            return 1.0 + 0.5 * (max_dp - self.ET_LOCK_THRESHOLD) / (self.MEMBRANE_RUPTURE_THRESHOLD - self.ET_LOCK_THRESHOLD)
    
    def _calculate_duration_risk(self, locked_duration: float) -> float:
        """Calculate time-based risk with physiological considerations"""
        # Exponential risk increase with duration
        return 1.0 - np.exp(-3.0 * locked_duration)
    
    def _calculate_phase_risk(self, phase_analysis: Dict[str, float]) -> float:
        """Calculate phase-specific risk considering physiological differences"""
        # Descent phase weighted more heavily due to increased difficulty
        ascent_risk = self._calculate_pressure_risk(phase_analysis['ascent_max_dp']) * 0.3
        descent_risk = self._calculate_pressure_risk(phase_analysis['descent_max_dp']) * 0.5
        cruise_risk = self._calculate_pressure_risk(phase_analysis['cruise_max_dp']) * 0.2
        return ascent_risk + descent_risk + cruise_risk
    
    def _calculate_dysfunction_factor(self, dysfunction: float) -> float:
        """Calculate dysfunction impact with physiological basis"""
        if dysfunction < 0.3:  # Normal to mild
            return 1.0 + dysfunction
        elif dysfunction < 0.6:  # Moderate
            return 1.3 + 2.0 * (dysfunction - 0.3)
        else:  # Severe
            return 1.9 + 3.0 * (dysfunction - 0.6)
    
    def _calculate_risk_confidence_interval(self, 
                                         pressure_data: np.ndarray, 
                                         dysfunction_factor: float) -> Tuple[float, float]:
        """Calculate confidence intervals using bootstrap"""
        bootstrap_risks = []
        for _ in range(self.BOOTSTRAP_SAMPLES):
            sample = np.random.choice(pressure_data, size=len(pressure_data), replace=True)
            max_dp = np.max(np.abs(sample))
            risk = self._calculate_pressure_risk(max_dp) * dysfunction_factor
            bootstrap_risks.append(risk)
        
        ci_lower = np.percentile(bootstrap_risks, (1 - self.CONFIDENCE_LEVEL) * 50)
        ci_upper = np.percentile(bootstrap_risks, (1 + self.CONFIDENCE_LEVEL) * 50)
        return ci_lower, ci_upper
    
    def generate_analysis_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive statistical analysis report"""
        report = {
            'summary_stats': df.describe(),
            'correlations': df.corr(),
            'risk_by_dysfunction': df.groupby('et_dysfunction')['risk_score'].agg(['mean', 'std', 'count']),
            'risk_by_altitude': df.groupby('cruise_altitude')['risk_score'].agg(['mean', 'std', 'count']),
            'phase_analysis': {
                'ascent': df.groupby('ascent_rate')['risk_score'].mean(),
                'descent': df.groupby('descent_rate')['risk_score'].mean()
            }
        }
        
        # Statistical tests
        report['statistical_tests'] = {
            'dysfunction_effect': stats.f_oneway(*[group['risk_score'].values 
                for name, group in df.groupby('et_dysfunction')]),
            'altitude_effect': stats.f_oneway(*[group['risk_score'].values 
                for name, group in df.groupby('cruise_altitude')]),
            'rate_correlations': {
                'ascent': stats.pearsonr(df['ascent_rate'], df['risk_score']),
                'descent': stats.pearsonr(df['descent_rate'], df['risk_score'])
            }
        }
        
        return report
    
    def plot_analysis_results(self, df: pd.DataFrame, save_path: str = None):
        """Generate comprehensive visualization of analysis results"""
        fig = plt.figure(figsize=(20, 15))
        gs = plt.GridSpec(3, 3)
        
        # Risk vs ET Dysfunction
        ax1 = fig.add_subplot(gs[0, 0])
        sns.boxplot(x='et_dysfunction', y='risk_score', data=df, ax=ax1)
        ax1.set_title('Risk Score vs ET Dysfunction')
        
        # Risk vs Altitude
        ax2 = fig.add_subplot(gs[0, 1])
        sns.scatterplot(x='cruise_altitude', y='risk_score', 
                       hue='et_dysfunction', data=df, ax=ax2)
        ax2.set_title('Risk Score vs Cruise Altitude')
        
        # Risk vs Rates
        ax3 = fig.add_subplot(gs[0, 2])
        sns.scatterplot(x='descent_rate', y='risk_score', 
                       hue='et_dysfunction', data=df, ax=ax3)
        ax3.set_title('Risk Score vs Descent Rate')
        
        # Pressure Distributions
        ax4 = fig.add_subplot(gs[1, 0])
        sns.histplot(data=df, x='max_pressure_differential', bins=30, ax=ax4)
        ax4.axvline(self.PASSIVE_OPENING_THRESHOLD, color='r', linestyle='--')
        ax4.axvline(self.ET_LOCK_THRESHOLD, color='r', linestyle='--')
        ax4.set_title('Pressure Differential Distribution')
        
        # Risk Score Distribution
        ax5 = fig.add_subplot(gs[1, 1])
        sns.histplot(data=df, x='risk_score', bins=30, ax=ax5)
        ax5.set_title('Risk Score Distribution')
        
        # Phase Analysis
        ax6 = fig.add_subplot(gs[1, 2])
        phase_data = pd.melt(df[['ascent_max_dp', 'descent_max_dp', 'cruise_max_dp']])
        sns.boxplot(x='variable', y='value', data=phase_data, ax=ax6)
        ax6.set_title('Pressure by Flight Phase')
        
        # Correlation Heatmap
        ax7 = fig.add_subplot(gs[2, :])
        correlation_matrix = df.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax7)
        ax7.set_title('Correlation Matrix')
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
        plt.close()

def run_comprehensive_analysis(
    ascent_rates: List[float] = [1000, 2000, 3000],
    cruise_altitudes: List[float] = [25000],
    descent_rates: List[float] = [1000, 2000, 3000, 6000, 12000, 18000],
    et_dysfunctions: List[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    n_iterations: int = 10
) -> Tuple[pd.DataFrame, Dict]:
    """Run comprehensive analysis with multiple simulations"""
    analyzer = SimulationAnalysis()
    
    # Run simulations
    results_df = analyzer.run_batch_simulation(
        ascent_rates=ascent_rates,
        descent_rates=descent_rates,
        cruise_altitudes=cruise_altitudes,
        et_dysfunctions=et_dysfunctions,
        n_iterations=n_iterations
    )
    
    # Perform statistical analysis
    stats_results = analyzer.generate_analysis_report(results_df)
    
    # Generate visualizations
    analyzer.plot_analysis_results(results_df)
    
    return results_df, stats_results

if __name__ == "__main__":
    # Example usage
    results_df, stats = run_comprehensive_analysis()
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(results_df.describe())
    
    # Print ANOVA results
    print("\nANOVA Results:")
    print(f"F-statistic: {stats['anova_results']['f_statistic']:.2f}")
    print(f"p-value: {stats['anova_results']['p_value']:.4f}") 