"""
Test script for analyzing relationships between key parameters and barotrauma risk.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from sklearn.metrics import r2_score, mean_squared_error
import logging
from typing import Dict, Tuple, List
from scipy.integrate import solve_ivp
import warnings

from .barotrauma_integrated_model import IntegratedBarotraumaModel
from .flight_profile_analyzer import FlightProfile, FlightProfileAnalyzer
from .clinical_risk_analyzer import ClinicalRiskAnalyzer, PatientProfile

class ModelRelationshipTester:
    """Test and visualize relationships between model parameters."""
    
    def __init__(self, model: IntegratedBarotraumaModel):
        self.model = model
        self.flight_analyzer = FlightProfileAnalyzer(model)
        self.clinical_analyzer = ClinicalRiskAnalyzer(model)
        self.logger = logging.getLogger(__name__)
        
        # Define test parameters
        self.et_dysfunction_range = np.linspace(0, 1, 21)
        self.rate_range = np.linspace(1000, 4000, 16)
        self.altitude_range = np.linspace(20000, 40000, 11)
        
        # Output directory
        self.output_dir = Path("test_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # Update simulation parameters with physiologically accurate values
        self.simulation_params = {
            'time_step': 0.1,  # seconds (finer resolution for accurate pressure changes)
            'max_time': 1800,  # seconds (30 min - typical flight phase duration)
            'solver_method': 'RK45',  # Runge-Kutta 4(5) - good for stiff equations
            'rtol': 1e-6,
            'atol': 1e-8,
            'max_step': 0.5  # seconds (limit step size for stability)
        }
        
        # Update physiological constraints based on literature
        self.phys_constraints = {
            'pressure': {
                'max_diff': 200,     # mmHg (maximum sustainable pressure differential)
                'warning': 100,      # mmHg (warning threshold)
                'rate_max': 50,      # mmHg/s (maximum safe rate of change)
                'equilibration': 15  # mmHg (normal equilibration threshold)
            },
            'volume': {
                'tym_min': 0.5e-3,   # L (minimum tympanic volume)
                'tym_max': 2.0e-3,   # L (maximum tympanic volume)
                'mas_min': 3.0e-3,   # L (minimum mastoid volume)
                'mas_max': 12.0e-3,  # L (maximum mastoid volume)
                'rate_max': 0.1e-3   # L/s (maximum volume change rate)
            },
            'et': {
                'dysfunction_range': (0, 1),
                'opening_pressure': (5, 15),    # mmHg
                'closing_pressure': (-5, 5),    # mmHg
                'opening_duration': (0.2, 0.5)  # seconds
            },
            'gas_exchange': {
                'O2_range': (0.005, 0.025),    # mol/s
                'CO2_range': (0.015, 0.035),   # mol/s
                'N2_range': (0.0005, 0.002),   # mol/s
                'H2O_range': (0.025, 0.045)    # mol/s
            }
        }
    
    def analyze_et_dysfunction_relationship(self) -> Dict:
        """Analyze relationship between ET dysfunction and barotrauma risk."""
        results = []
        warnings.filterwarnings('error')  # Treat warnings as errors for numerical issues
        
        for et_score in self.et_dysfunction_range:
            try:
                # Create simulation scenario
                scenario = self._create_simulation_scenario(et_score)
                
                # Create time array for simulation
                time_array = np.arange(0, self.simulation_params['max_time'], 
                                     self.simulation_params['time_step'])
                
                # Run simulation
                sim_result = self.model._simulate_scenario(scenario)
                
                if sim_result is None:
                    self.logger.warning(f"Simulation failed for ET score {et_score}")
                    continue
                
                # Validate results
                valid, messages = self._validate_simulation_results(
                    sim_result.time,
                    sim_result.pressure_history,
                    sim_result.volume_history
                )
                
                if not valid:
                    self.logger.warning(f"Invalid results for ET score {et_score}: {messages}")
                    continue
                
                # Calculate risk metrics
                risk_metrics = self._calculate_risk_metrics(sim_result)
                
                results.append({
                    'et_dysfunction': et_score,
                    'max_pressure': np.max(np.abs(sim_result.pressure_history)),
                    'volume_change': (np.max(sim_result.volume_history) - 
                                    np.min(sim_result.volume_history)) * 1e6,  # µL
                    'risk_score': risk_metrics['risk_score'],
                    'confidence': risk_metrics['confidence']
                })
                
            except Exception as e:
                self.logger.error(f"Error processing ET score {et_score}: {str(e)}")
                continue
        
        if not results:
            self.logger.error("No valid results obtained from analysis")
            return {'data': pd.DataFrame(), 'stats': {}}
        
        df = pd.DataFrame(results)
        
        # Statistical analysis with error handling
        try:
            stats_results = {
                'correlation': stats.pearsonr(df['et_dysfunction'], df['risk_score'])[0],
                'r2': r2_score(df['et_dysfunction'], df['risk_score']),
                'slope': np.polyfit(df['et_dysfunction'], df['risk_score'], 1)[0]
            }
        except Exception as e:
            self.logger.error(f"Statistical analysis failed: {str(e)}")
            stats_results = {}
        
        # Plot results with error handling
        try:
            self._plot_et_dysfunction_results(df, stats_results)
        except Exception as e:
            self.logger.error(f"Plotting failed: {str(e)}")
        
        return {'data': df, 'stats': stats_results}
    
    def _plot_et_dysfunction_results(self, df: pd.DataFrame, stats_results: Dict):
        """Helper method for plotting ET dysfunction results."""
        plt.figure(figsize=(12, 8))
        
        # Plot scatter points
        sns.scatterplot(data=df, x='et_dysfunction', y='risk_score')
        
        # Add regression line if we have enough data
        if len(df) > 2:
            sns.regplot(data=df, x='et_dysfunction', y='risk_score', 
                       scatter=False, color='red')
        
        plt.title('ET Dysfunction vs Barotrauma Risk')
        plt.xlabel('ET Dysfunction Score')
        plt.ylabel('Risk Score')
        
        # Add statistical annotations if available
        if stats_results:
            annotation_text = (
                f"Correlation: {stats_results.get('correlation', 'N/A'):.3f}\n"
                f"R²: {stats_results.get('r2', 'N/A'):.3f}\n"
                f"Slope: {stats_results.get('slope', 'N/A'):.3f}"
            )
            plt.text(0.05, 0.95, annotation_text,
                    transform=plt.gca().transAxes,
                    bbox=dict(facecolor='white', alpha=0.8))
        
        plt.grid(True)
        plt.tight_layout()
        
        try:
            plt.savefig(self.output_dir / 'et_dysfunction_relationship.pdf')
        except Exception as e:
            self.logger.error(f"Failed to save plot: {str(e)}")
        finally:
            plt.close()
    
    def analyze_rate_interactions(self) -> Dict:
        """Analyze interaction between climb/descent rates and ET dysfunction."""
        results = []
        
        for et_score in [0.2, 0.5, 0.8]:  # Low, medium, high dysfunction
            for rate in self.rate_range:
                # Create flight profile
                profile = FlightProfile(
                    name=f'Test Profile {rate:.0f}',
                    initial_altitude=0,
                    final_altitude=0,
                    climb_rate=rate,
                    descent_rate=rate,
                    cruise_duration=30,
                    cruise_altitude=35000
                )
                
                # Create patient
                patient = PatientProfile(
                    age=35,
                    et_dysfunction_score=et_score,
                    previous_barotrauma=False,
                    chronic_conditions=[],
                    anatomical_factors={'mastoid_volume_ratio': 1.0},
                    medications=[]
                )
                
                # Analyze risk
                risk_analysis = self.clinical_analyzer.analyze_patient_risk(
                    patient, profile
                )
                
                results.append({
                    'et_dysfunction': et_score,
                    'rate': rate,
                    'risk_score': risk_analysis['combined_risk']
                })
        
        df = pd.DataFrame(results)
        
        # Statistical analysis
        stats_results = {}
        for et_score in [0.2, 0.5, 0.8]:
            subset = df[df['et_dysfunction'] == et_score]
            stats_results[f'et_{et_score}'] = {
                'correlation': stats.pearsonr(subset['rate'], subset['risk_score'])[0],
                'r2': r2_score(subset['rate'], subset['risk_score']),
                'slope': np.polyfit(subset['rate'], subset['risk_score'], 1)[0]
            }
        
        # Plot results
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=df, x='rate', y='risk_score', 
                       hue='et_dysfunction', style='et_dysfunction')
        
        plt.title('Rate vs Risk Score by ET Dysfunction Level')
        plt.xlabel('Rate (ft/min)')
        plt.ylabel('Risk Score')
        
        plt.savefig(self.output_dir / 'rate_interaction.pdf')
        plt.close()
        
        return {'data': df, 'stats': stats_results}
    
    def analyze_altitude_sensitivity(self) -> Dict:
        """Analyze sensitivity to maximum altitude."""
        results = []
        
        for altitude in self.altitude_range:
            for et_score in [0.2, 0.5, 0.8]:
                profile = FlightProfile(
                    name=f'Alt Test {altitude:.0f}',
                    initial_altitude=0,
                    final_altitude=0,
                    climb_rate=2000,
                    descent_rate=2000,
                    cruise_duration=30,
                    cruise_altitude=altitude
                )
                
                patient = PatientProfile(
                    age=35,
                    et_dysfunction_score=et_score,
                    previous_barotrauma=False,
                    chronic_conditions=[],
                    anatomical_factors={'mastoid_volume_ratio': 1.0},
                    medications=[]
                )
                
                risk_analysis = self.clinical_analyzer.analyze_patient_risk(
                    patient, profile
                )
                
                results.append({
                    'altitude': altitude,
                    'et_dysfunction': et_score,
                    'risk_score': risk_analysis['combined_risk']
                })
        
        df = pd.DataFrame(results)
        
        # Plot results
        plt.figure(figsize=(12, 8))
        sns.lineplot(data=df, x='altitude', y='risk_score', 
                    hue='et_dysfunction', style='et_dysfunction',
                    markers=True)
        
        plt.title('Altitude vs Risk Score by ET Dysfunction Level')
        plt.xlabel('Maximum Altitude (ft)')
        plt.ylabel('Risk Score')
        
        plt.savefig(self.output_dir / 'altitude_sensitivity.pdf')
        plt.close()
        
        return {'data': df}
    
    def generate_statistical_report(self, results: Dict) -> str:
        """Generate comprehensive statistical report."""
        report = ["Statistical Analysis Report", "=" * 40, "\n"]
        
        # ET dysfunction relationship
        if 'et_dysfunction_relationship' in results:
            et_stats = results['et_dysfunction_relationship']['stats']
            report.extend([
                "ET Dysfunction Analysis:",
                "-" * 20,
                f"Correlation coefficient: {et_stats['correlation']:.3f}",
                f"R-squared value: {et_stats['r2']:.3f}",
                f"Linear relationship slope: {et_stats['slope']:.3f}",
                "\n"
            ])
        
        # Rate interaction analysis
        if 'rate_interaction' in results:
            rate_stats = results['rate_interaction']['stats']
            report.extend(["Rate Interaction Analysis:", "-" * 20])
            for et_level, stats in rate_stats.items():
                report.extend([
                    f"\nET Dysfunction Level {et_level}:",
                    f"  Correlation: {stats['correlation']:.3f}",
                    f"  R-squared: {stats['r2']:.3f}",
                    f"  Slope: {stats['slope']:.3f}"
                ])
        
        report_text = "\n".join(report)
        with open(self.output_dir / 'statistical_report.txt', 'w') as f:
            f.write(report_text)
        
        return report_text
    
    def _calculate_risk_metrics(self, sim_result) -> Dict:
        """
        Calculate comprehensive risk metrics from simulation results.
        
        Args:
            sim_result: Simulation result object containing pressure and volume histories
        
        Returns:
            Dictionary containing risk metrics and confidence scores
        """
        # Extract time series data
        pressure = sim_result.pressure_history
        volume = sim_result.volume_history
        time = sim_result.time
        
        # Calculate pressure-based metrics
        pressure_metrics = {
            'max_diff': np.max(np.abs(pressure)),
            'mean_diff': np.mean(np.abs(pressure)),
            'std_diff': np.std(pressure),
            'rate_max': np.max(np.abs(np.gradient(pressure, time))),
            'time_above_warning': np.sum(np.abs(pressure) > 
                                       self.phys_constraints['pressure']['warning']) * \
                                np.mean(np.diff(time))
        }
        
        # Calculate volume-based metrics
        volume_change = np.max(volume) - np.min(volume)
        volume_rate = np.gradient(volume, time)
        volume_metrics = {
            'total_change': volume_change,
            'max_rate': np.max(np.abs(volume_rate)),
            'mean_rate': np.mean(np.abs(volume_rate)),
            'excursion_ratio': volume_change / np.mean(volume)
        }
        
        # Calculate risk components
        pressure_risk = self._calculate_pressure_risk(pressure_metrics)
        volume_risk = self._calculate_volume_risk(volume_metrics)
        rate_risk = self._calculate_rate_risk(pressure_metrics['rate_max'], 
                                            volume_metrics['max_rate'])
        
        # Calculate confidence based on physiological bounds
        confidence = self._calculate_confidence(pressure_metrics, volume_metrics)
        
        # Combine risk components with physiological weighting
        risk_score = (
            0.5 * pressure_risk +    # Pressure differential is primary risk factor
            0.3 * volume_risk +      # Volume changes are secondary
            0.2 * rate_risk         # Rate of change contributes to acute risk
        )
        
        return {
            'risk_score': np.clip(risk_score, 0, 1),
            'confidence': confidence,
            'components': {
                'pressure_risk': pressure_risk,
                'volume_risk': volume_risk,
                'rate_risk': rate_risk
            },
            'metrics': {
                'pressure': pressure_metrics,
                'volume': volume_metrics
            }
        }
    
    def _calculate_pressure_risk(self, pressure_metrics: Dict) -> float:
        """Calculate pressure-based risk component."""
        # Define pressure thresholds based on literature
        critical_pressure = self.phys_constraints['pressure']['max_diff']
        warning_pressure = self.phys_constraints['pressure']['warning']
        
        # Calculate normalized pressure risk
        max_pressure_risk = np.clip(pressure_metrics['max_diff'] / critical_pressure, 0, 1)
        
        # Add time-weighted component for sustained pressure
        time_weight = np.clip(pressure_metrics['time_above_warning'] / 60, 0, 1)  # Normalize to 1 minute
        
        # Combine immediate and sustained risks
        pressure_risk = 0.7 * max_pressure_risk + 0.3 * time_weight
        
        # Add penalty for rapid fluctuations
        if pressure_metrics['std_diff'] > warning_pressure / 4:
            pressure_risk *= 1.2
        
        return np.clip(pressure_risk, 0, 1)
    
    def _calculate_volume_risk(self, volume_metrics: Dict) -> float:
        """Calculate volume-based risk component."""
        # Define volume change thresholds
        max_safe_change = (self.phys_constraints['volume']['tym_max'] - 
                          self.phys_constraints['volume']['tym_min'])
        
        # Calculate normalized volume risk
        volume_change_risk = np.clip(volume_metrics['total_change'] / max_safe_change, 0, 1)
        
        # Add rate component
        rate_risk = np.clip(volume_metrics['max_rate'] / 
                           self.phys_constraints['volume']['rate_max'], 0, 1)
        
        # Combine with emphasis on total change
        volume_risk = 0.7 * volume_change_risk + 0.3 * rate_risk
        
        # Add penalty for excessive excursion
        if volume_metrics['excursion_ratio'] > 0.3:  # >30% volume change
            volume_risk *= 1.2
        
        return np.clip(volume_risk, 0, 1)
    
    def _calculate_rate_risk(self, pressure_rate: float, volume_rate: float) -> float:
        """Calculate rate-of-change risk component."""
        # Normalize rates to their physiological limits
        norm_pressure_rate = np.clip(pressure_rate / 
                                    self.phys_constraints['pressure']['rate_max'], 0, 1)
        norm_volume_rate = np.clip(volume_rate / 
                                  self.phys_constraints['volume']['rate_max'], 0, 1)
        
        # Combine with emphasis on pressure rate
        rate_risk = 0.7 * norm_pressure_rate + 0.3 * norm_volume_rate
        
        return np.clip(rate_risk, 0, 1)
    
    def _calculate_confidence(self, pressure_metrics: Dict, volume_metrics: Dict) -> float:
        """Calculate confidence score for risk assessment."""
        confidence = 1.0
        
        # Reduce confidence for extreme values
        if pressure_metrics['max_diff'] > 0.9 * self.phys_constraints['pressure']['max_diff']:
            confidence *= 0.8
        
        if volume_metrics['total_change'] > 0.9 * (self.phys_constraints['volume']['tym_max'] - 
                                                  self.phys_constraints['volume']['tym_min']):
            confidence *= 0.8
        
        # Reduce confidence for high rates of change
        if pressure_metrics['rate_max'] > 0.9 * self.phys_constraints['pressure']['rate_max']:
            confidence *= 0.9
        
        if volume_metrics['max_rate'] > 0.9 * self.phys_constraints['volume']['rate_max']:
            confidence *= 0.9
        
        # Reduce confidence for high variability
        if pressure_metrics['std_diff'] > 0.5 * pressure_metrics['mean_diff']:
            confidence *= 0.9
        
        return np.clip(confidence, 0.2, 1.0)
    
    def _create_simulation_scenario(self, et_score: float, rate: float = 2000) -> Dict:
        """
        Create a physiologically valid simulation scenario.
        
        Args:
            et_score: ET dysfunction score (0-1)
            rate: Climb/descent rate in ft/min
        
        Returns:
            Dictionary containing simulation parameters
        """
        return {
            'initial_altitude_ft': 0,
            'final_altitude_ft': 35000,
            'climb_rate_ft_min': rate,
            'descent_rate_ft_min': rate,
            'cruise_duration_min': 20,
            'et_dysfunction': et_score,
            'V_tym': 1.0e-3,  # L
            'V_mas': 7.75e-3,  # L
            'mastoid_compliance': 2e-5,  # L/mmHg
            'k_MEM': {
                'O2': 0.015,   # mol/s
                'CO2': 0.025,  # mol/s
                'N2': 0.0008,  # mol/s
                'H2O': 0.035   # mol/s
            }
        }
    
    def _validate_simulation_results(self, time: np.ndarray, 
                                   pressure: np.ndarray, 
                                   volume: np.ndarray) -> Tuple[bool, List[str]]:
        """
        Validate simulation results against physiological constraints.
        
        Args:
            time: Time points array
            pressure: Pressure history array
            volume: Volume history array
        
        Returns:
            Tuple of (is_valid, list of validation messages)
        """
        valid = True
        messages = []
        
        # Check pressure constraints
        max_pressure_diff = np.max(np.abs(pressure))
        if max_pressure_diff > self.phys_constraints['pressure']['max_diff']:
            valid = False
            messages.append(f"Pressure differential {max_pressure_diff:.1f} mmHg exceeds maximum")
        
        # Check pressure rate
        pressure_rate = np.abs(np.gradient(pressure, time))
        max_rate = np.max(pressure_rate)
        if max_rate > self.phys_constraints['pressure']['rate_max']:
            valid = False
            messages.append(f"Pressure rate {max_rate:.1f} mmHg/s exceeds maximum")
        
        # Check volume constraints
        if np.any(volume < self.phys_constraints['volume']['tym_min']) or \
           np.any(volume > self.phys_constraints['volume']['mas_max']):
            valid = False
            messages.append("Volume outside physiological range")
        
        # Check volume rate
        volume_rate = np.abs(np.gradient(volume, time))
        max_vol_rate = np.max(volume_rate)
        if max_vol_rate > self.phys_constraints['volume']['rate_max']:
            valid = False
            messages.append(f"Volume change rate {max_vol_rate*1e6:.1f} µL/s exceeds maximum")
        
        return valid, messages

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Initialize model and tester
    model = IntegratedBarotraumaModel(physical_weight=0.6)
    tester = ModelRelationshipTester(model)
    
    logger.info("Analyzing ET dysfunction relationship")
    et_results = tester.analyze_et_dysfunction_relationship()
    
    logger.info("Analyzing rate interactions")
    rate_results = tester.analyze_rate_interactions()
    
    logger.info("Analyzing altitude sensitivity")
    altitude_results = tester.analyze_altitude_sensitivity()
    
    # Generate statistical report
    results = {
        'et_dysfunction_relationship': et_results,
        'rate_interaction': rate_results,
        'altitude_sensitivity': altitude_results
    }
    
    report = tester.generate_statistical_report(results)
    logger.info("\nStatistical Analysis Report:")
    logger.info("\n" + report)

if __name__ == "__main__":
    main() 