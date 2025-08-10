"""
Analysis module for flight profiles and their impact on barotrauma risk.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from dataclasses import dataclass
from scipy.integrate import trapezoid

from .barotrauma_integrated_model import IntegratedBarotraumaModel
from .barotrauma_analyzer import AnalysisScenario

@dataclass
class FlightProfile:
    """Container for flight profile parameters."""
    name: str
    initial_altitude: float  # ft
    final_altitude: float   # ft
    climb_rate: float      # ft/min
    descent_rate: float    # ft/min
    cruise_duration: float # min
    cruise_altitude: float # ft
    
    def validate(self) -> bool:
        """Validate flight profile parameters."""
        return (
            0 <= self.initial_altitude <= 45000 and
            0 <= self.final_altitude <= 45000 and
            500 <= self.climb_rate <= 4000 and
            500 <= self.descent_rate <= 4000 and
            0 <= self.cruise_duration <= 1000 and
            0 <= self.cruise_altitude <= 45000
        )

class FlightProfileAnalyzer:
    """Analyzer for flight profiles and their impact on barotrauma risk."""
    
    def __init__(self, model: IntegratedBarotraumaModel):
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Standard flight profiles
        self.standard_profiles = {
            'commercial': FlightProfile(
                name='Commercial Flight',
                initial_altitude=0,
                final_altitude=0,
                climb_rate=2000,
                descent_rate=2000,
                cruise_duration=180,
                cruise_altitude=35000
            ),
            'military': FlightProfile(
                name='Military Training',
                initial_altitude=0,
                final_altitude=0,
                climb_rate=3000,
                descent_rate=3000,
                cruise_duration=45,
                cruise_altitude=25000
            ),
            'emergency': FlightProfile(
                name='Emergency Descent',
                initial_altitude=35000,
                final_altitude=0,
                climb_rate=2000,
                descent_rate=3500,
                cruise_duration=5,
                cruise_altitude=35000
            )
        }
    
    def analyze_profile_risk(self, profile: FlightProfile, 
                           et_dysfunction_levels: Optional[List[float]] = None) -> pd.DataFrame:
        """Analyze barotrauma risk for a flight profile across ET dysfunction levels."""
        if et_dysfunction_levels is None:
            et_dysfunction_levels = np.linspace(0, 1, 11)
        
        results = []
        for et_level in et_dysfunction_levels:
            scenario = self._create_analysis_scenario(profile, et_level)
            prediction = self.model.analyze_prediction_confidence(
                self._scenario_to_dict(scenario)
            )
            
            if prediction['confidence'] > 0:
                results.append({
                    'et_dysfunction': et_level,
                    'risk_score': prediction['risk_score'],
                    'confidence': prediction['confidence'],
                    'profile_name': profile.name,
                    'max_altitude': profile.cruise_altitude,
                    'climb_rate': profile.climb_rate,
                    'descent_rate': profile.descent_rate
                })
        
        return pd.DataFrame(results)
    
    def compare_profiles(self, profiles: Optional[List[FlightProfile]] = None) -> pd.DataFrame:
        """Compare barotrauma risk across different flight profiles."""
        if profiles is None:
            profiles = list(self.standard_profiles.values())
        
        results = []
        for profile in profiles:
            profile_results = self.analyze_profile_risk(profile)
            results.append(profile_results)
        
        return pd.concat(results, ignore_index=True)
    
    def analyze_descent_strategies(self, base_profile: FlightProfile,
                                 descent_rates: Optional[List[float]] = None) -> pd.DataFrame:
        """Analyze impact of different descent strategies."""
        if descent_rates is None:
            descent_rates = np.linspace(1000, 4000, 7)
        
        results = []
        for rate in descent_rates:
            modified_profile = FlightProfile(
                name=f"Descent Rate {rate:.0f}",
                initial_altitude=base_profile.initial_altitude,
                final_altitude=base_profile.final_altitude,
                climb_rate=base_profile.climb_rate,
                descent_rate=rate,
                cruise_duration=base_profile.cruise_duration,
                cruise_altitude=base_profile.cruise_altitude
            )
            
            profile_results = self.analyze_profile_risk(modified_profile)
            results.append(profile_results)
        
        return pd.concat(results, ignore_index=True)
    
    def _create_analysis_scenario(self, profile: FlightProfile, 
                                et_dysfunction: float) -> AnalysisScenario:
        """Create analysis scenario from flight profile."""
        return AnalysisScenario(
            name=profile.name,
            et_dysfunction=et_dysfunction,
            altitude_profile={
                'initial_altitude_ft': profile.initial_altitude,
                'final_altitude_ft': profile.final_altitude,
                'climb_rate_ft_min': profile.climb_rate,
                'descent_rate_ft_min': profile.descent_rate,
                'cruise_duration_min': profile.cruise_duration
            },
            gas_exchange_rates={
                'O2': 0.015,
                'CO2': 0.025,
                'N2': 0.0008,
                'H2O': 0.035
            },
            volumes={
                'V_tym': 1.0e-3,
                'V_mas': 7.75e-3
            }
        )
    
    def _scenario_to_dict(self, scenario: AnalysisScenario) -> Dict:
        """Convert analysis scenario to dictionary format."""
        return {
            'et_dysfunction': scenario.et_dysfunction,
            **scenario.altitude_profile,
            'k_MEM': scenario.gas_exchange_rates,
            **scenario.volumes
        }
    
    def plot_profile_comparison(self, results: pd.DataFrame, 
                              save_dir: Optional[Path] = None):
        """Generate comparison plots for flight profiles."""
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Plot 1: Risk scores across ET dysfunction levels
        plt.figure(figsize=(12, 8))
        sns.lineplot(data=results, x='et_dysfunction', y='risk_score', 
                    hue='profile_name', style='profile_name', markers=True)
        plt.title('Risk Score by ET Dysfunction Level')
        plt.xlabel('ET Dysfunction')
        plt.ylabel('Risk Score')
        plt.grid(True)
        
        if save_dir:
            plt.savefig(save_dir / 'profile_risk_comparison.pdf')
        plt.close()
        
        # Plot 2: Risk distribution by profile
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=results, x='profile_name', y='risk_score')
        plt.title('Risk Score Distribution by Flight Profile')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(save_dir / 'risk_distribution.pdf')
        plt.close()
    
    def plot_descent_analysis(self, results: pd.DataFrame,
                            save_dir: Optional[Path] = None):
        """Generate plots for descent strategy analysis."""
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Plot risk vs descent rate
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=results, x='descent_rate', y='risk_score', 
                       hue='et_dysfunction', size='confidence')
        plt.title('Risk Score vs Descent Rate')
        plt.xlabel('Descent Rate (ft/min)')
        plt.ylabel('Risk Score')
        plt.grid(True)
        
        if save_dir:
            plt.savefig(save_dir / 'descent_rate_analysis.pdf')
        plt.close()
    
    def generate_profile_report(self, results: pd.DataFrame,
                              save_path: Optional[Path] = None) -> str:
        """Generate detailed report of flight profile analysis."""
        report = ["Flight Profile Analysis Report", "=" * 40, ""]
        
        # Overall statistics
        report.extend([
            "Overall Statistics:",
            "-" * 20,
            f"Number of profiles analyzed: {results['profile_name'].nunique()}",
            f"Overall mean risk score: {results['risk_score'].mean():.3f}",
            f"Overall max risk score: {results['risk_score'].max():.3f}",
            ""
        ])
        
        # Profile-specific statistics
        report.extend(["Profile Statistics:", "-" * 20])
        for profile in results['profile_name'].unique():
            profile_data = results[results['profile_name'] == profile]
            report.extend([
                f"\n{profile}:",
                f"  Mean risk score: {profile_data['risk_score'].mean():.3f}",
                f"  Max risk score: {profile_data['risk_score'].max():.3f}",
                f"  Mean confidence: {profile_data['confidence'].mean():.3f}"
            ])
        
        # Risk factors
        report.extend([
            "\nRisk Factors:",
            "-" * 15,
            f"Correlation with descent rate: {results['descent_rate'].corr(results['risk_score']):.3f}",
            f"Correlation with max altitude: {results['max_altitude'].corr(results['risk_score']):.3f}"
        ])
        
        report_text = "\n".join(report)
        if save_path:
            save_path.write_text(report_text)
        
        return report_text 
    
    def _calculate_exposure_metrics(self, time: np.ndarray, values: np.ndarray, 
                                  threshold: float) -> float:
        """Calculate exposure metrics using trapezoid integration."""
        mask = values > threshold
        if not np.any(mask):
            return 0.0
        return trapezoid(values[mask], time[mask]) 