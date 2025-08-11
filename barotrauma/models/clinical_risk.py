"""
Clinical risk analyzer for patient-specific barotrauma risk assessment.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from dataclasses import dataclass

from .barotrauma_integrated_model import IntegratedBarotraumaModel
from .flight_profile_analyzer import FlightProfile, FlightProfileAnalyzer

@dataclass
class PatientProfile:
    """Container for patient-specific risk factors."""
    age: int
    et_dysfunction_score: float  # 0-1 scale
    previous_barotrauma: bool
    chronic_conditions: List[str]
    anatomical_factors: Dict[str, float]  # e.g., mastoid volume variations
    medications: List[str]
    
    def validate(self) -> bool:
        """Validate patient profile parameters."""
        return (
            0 <= self.age <= 120 and
            0 <= self.et_dysfunction_score <= 1 and
            isinstance(self.previous_barotrauma, bool) and
            all(isinstance(v, float) for v in self.anatomical_factors.values())
        )

class ClinicalRiskAnalyzer:
    """Analyzer for patient-specific barotrauma risk assessment."""
    
    def __init__(self, model: IntegratedBarotraumaModel):
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.flight_analyzer = FlightProfileAnalyzer(model)
        
        # Risk factor weights based on clinical literature
        self.risk_weights = {
            'age': 0.2,
            'et_dysfunction': 0.4,
            'previous_barotrauma': 0.15,
            'chronic_conditions': 0.15,
            'anatomical_factors': 0.1
        }
        
        # Define high-risk conditions
        self.high_risk_conditions = {
            'chronic_sinusitis',
            'allergic_rhinitis',
            'craniofacial_abnormalities',
            'recent_uri'
        }
        
        # Define risk-modifying medications
        self.risk_medications = {
            'increase': ['oral_decongestants', 'antihistamines'],
            'decrease': ['nasal_steroids', 'oral_steroids']
        }
    
    def analyze_patient_risk(self, patient: PatientProfile, 
                           flight_profile: FlightProfile) -> Dict:
        """
        Analyze barotrauma risk for specific patient and flight profile.
        
        Args:
            patient: PatientProfile object containing patient risk factors
            flight_profile: FlightProfile object for the planned flight
            
        Returns:
            Dictionary containing risk analysis results
        """
        # Calculate base risk score
        base_risk = self._calculate_base_risk(patient)
        
        # Analyze flight-specific risk
        flight_risk = self._analyze_flight_risk(patient, flight_profile)
        
        # Calculate combined risk score
        combined_risk = self._combine_risk_scores(base_risk, flight_risk)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(patient, flight_profile, combined_risk)
        
        return {
            'base_risk': base_risk,
            'flight_risk': flight_risk,
            'combined_risk': combined_risk,
            'risk_category': self._categorize_risk(combined_risk),
            'recommendations': recommendations,
            'contraindications': self._check_contraindications(patient, flight_profile)
        }
    
    def _calculate_base_risk(self, patient: PatientProfile) -> float:
        """Calculate baseline risk score from patient factors."""
        risk_score = 0.0
        
        # Age factor (increased risk for very young and elderly)
        age_risk = np.clip(abs(patient.age - 30) / 50, 0, 1)
        risk_score += age_risk * self.risk_weights['age']
        
        # ET dysfunction
        risk_score += patient.et_dysfunction_score * self.risk_weights['et_dysfunction']
        
        # Previous barotrauma
        if patient.previous_barotrauma:
            risk_score += self.risk_weights['previous_barotrauma']
        
        # Chronic conditions
        condition_risk = sum(1 for c in patient.chronic_conditions 
                           if c in self.high_risk_conditions)
        risk_score += (condition_risk / len(self.high_risk_conditions) * 
                      self.risk_weights['chronic_conditions'])
        
        # Anatomical factors
        if patient.anatomical_factors:
            anat_risk = np.mean([abs(v - 1) for v in patient.anatomical_factors.values()])
            risk_score += anat_risk * self.risk_weights['anatomical_factors']
        
        return np.clip(risk_score, 0, 1)
    
    def _analyze_flight_risk(self, patient: PatientProfile, 
                           flight_profile: FlightProfile) -> float:
        """Analyze risk specific to flight profile."""
        # Get base flight profile risk
        profile_results = self.flight_analyzer.analyze_profile_risk(
            flight_profile, 
            [patient.et_dysfunction_score]
        )
        
        flight_risk = profile_results['risk_score'].iloc[0]
        
        # Adjust for medications
        med_factor = self._calculate_medication_effect(patient.medications)
        flight_risk *= med_factor
        
        return np.clip(flight_risk, 0, 1)
    
    def _calculate_medication_effect(self, medications: List[str]) -> float:
        """Calculate medication effect on risk."""
        effect = 1.0
        
        for med in medications:
            if med in self.risk_medications['increase']:
                effect *= 1.2
            elif med in self.risk_medications['decrease']:
                effect *= 0.8
        
        return effect
    
    def _combine_risk_scores(self, base_risk: float, flight_risk: float) -> float:
        """Combine base and flight-specific risk scores."""
        # Use weighted geometric mean for combined risk
        return np.power(base_risk * flight_risk, 0.5)
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level."""
        if risk_score < 0.3:
            return "Low Risk"
        elif risk_score < 0.6:
            return "Moderate Risk"
        else:
            return "High Risk"
    
    def _check_contraindications(self, patient: PatientProfile, 
                               flight_profile: FlightProfile) -> List[str]:
        """Check for absolute and relative contraindications."""
        contraindications = []
        
        # Absolute contraindications
        if patient.et_dysfunction_score > 0.8:
            contraindications.append("Severe ET dysfunction")
        
        if any(c == 'acute_otitis_media' for c in patient.chronic_conditions):
            contraindications.append("Active ear infection")
        
        # Relative contraindications
        if patient.previous_barotrauma and flight_profile.cruise_altitude > 30000:
            contraindications.append("High altitude with previous barotrauma")
        
        if (patient.et_dysfunction_score > 0.6 and 
            flight_profile.descent_rate > 2500):
            contraindications.append("Rapid descent with moderate-severe ET dysfunction")
        
        return contraindications
    
    def _generate_recommendations(self, patient: PatientProfile,
                                flight_profile: FlightProfile,
                                risk_score: float) -> List[str]:
        """Generate patient-specific recommendations."""
        recommendations = []
        
        # Basic recommendations
        recommendations.append("Stay hydrated before and during flight")
        recommendations.append("Perform Valsalva maneuver during descent")
        
        # Risk-specific recommendations
        if risk_score > 0.3:
            recommendations.append("Consider using nasal decongestant before flight")
            
        if risk_score > 0.6:
            recommendations.append("Consider postponing non-essential flight")
            recommendations.append("Consult ENT specialist before flying")
        
        # Profile-specific recommendations
        if flight_profile.cruise_altitude > 30000:
            recommendations.append("Request gradual descent if possible")
        
        if patient.et_dysfunction_score > 0.5:
            recommendations.append("Use prophylactic medications as prescribed")
        
        return recommendations
    
    def plot_risk_analysis(self, patient: PatientProfile,
                          flight_profile: FlightProfile,
                          save_dir: Optional[Path] = None):
        """Generate visualization of risk analysis."""
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
        
        # Create risk factor breakdown plot
        plt.figure(figsize=(10, 6))
        risk_factors = {
            'ET Dysfunction': patient.et_dysfunction_score * self.risk_weights['et_dysfunction'],
            'Age Risk': self._calculate_age_risk(patient.age) * self.risk_weights['age'],
            'Previous Barotrauma': float(patient.previous_barotrauma) * self.risk_weights['previous_barotrauma'],
            'Conditions': len(set(patient.chronic_conditions) & self.high_risk_conditions) / 
                        len(self.high_risk_conditions) * self.risk_weights['chronic_conditions']
        }
        
        plt.bar(risk_factors.keys(), risk_factors.values())
        plt.title('Risk Factor Breakdown')
        plt.ylabel('Risk Contribution')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_dir:
            plt.savefig(save_dir / 'risk_breakdown.pdf')
        plt.close()
    
    def generate_clinical_report(self, patient: PatientProfile,
                               flight_profile: FlightProfile,
                               risk_analysis: Dict,
                               save_path: Optional[Path] = None) -> str:
        """Generate detailed clinical risk assessment report."""
        report = ["Clinical Risk Assessment Report", "=" * 40, ""]
        
        # Patient profile
        report.extend([
            "Patient Profile:",
            "-" * 15,
            f"Age: {patient.age}",
            f"ET Dysfunction Score: {patient.et_dysfunction_score:.2f}",
            f"Previous Barotrauma: {'Yes' if patient.previous_barotrauma else 'No'}",
            f"Chronic Conditions: {', '.join(patient.chronic_conditions)}",
            ""
        ])
        
        # Risk assessment
        report.extend([
            "Risk Assessment:",
            "-" * 15,
            f"Base Risk Score: {risk_analysis['base_risk']:.3f}",
            f"Flight-Specific Risk: {risk_analysis['flight_risk']:.3f}",
            f"Combined Risk Score: {risk_analysis['combined_risk']:.3f}",
            f"Risk Category: {risk_analysis['risk_category']}",
            ""
        ])
        
        # Contraindications
        if risk_analysis['contraindications']:
            report.extend([
                "Contraindications:",
                "-" * 17,
                *[f"- {c}" for c in risk_analysis['contraindications']],
                ""
            ])
        
        # Recommendations
        report.extend([
            "Recommendations:",
            "-" * 15,
            *[f"- {r}" for r in risk_analysis['recommendations']]
        ])
        
        report_text = "\n".join(report)
        if save_path:
            save_path.write_text(report_text)
        
        return report_text 