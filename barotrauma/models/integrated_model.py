"""
Integrated model combining physical simulation with machine learning for barotrauma prediction.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_validate
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score
import joblib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
from scipy.integrate import trapezoid

from .barotrauma_simulation_10 import BarotraumaSimulation, simulate_flight_profile

@dataclass
class SimulationResult:
    """Container for simulation results with validation."""
    pressure_history: np.ndarray
    volume_history: np.ndarray
    time: np.ndarray
    gas_exchange_rates: Dict[str, float]
    risk_score: float
    risk_category: str
    
    def validate(self) -> bool:
        """Validate simulation results are within physiological bounds."""
        try:
            return (
                np.all(np.abs(self.pressure_history) < 200) and  # mmHg
                np.all(self.volume_history > 0) and
                np.all(self.volume_history < 20e-3) and  # L
                all(0 <= rate <= 1e-3 for rate in self.gas_exchange_rates.values())
            )
        except Exception as e:
            logging.error(f"Validation error: {str(e)}")
            return False

class IntegratedBarotraumaModel:
    """Enhanced integrated model combining physical simulation with ML."""
    
    def __init__(self, physical_weight: float = 0.6):
        """Initialize the integrated model."""
        self.physical_weight = physical_weight
        self.ml_weight = 1 - physical_weight
        
        # Initialize ML components
        self.rf_classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_split=10,
            random_state=42
        )
        self.gb_classifier = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Calibrated models
        self.calibrated_rf = None
        self.calibrated_gb = None
        
        # Physical simulation components
        self.simulation_cache = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _simulate_scenario(self, scenario: Dict) -> Optional[SimulationResult]:
        """Run physical simulation for a scenario."""
        try:
            # Check cache first
            cache_key = str(sorted(scenario.items()))
            if cache_key in self.simulation_cache:
                return self.simulation_cache[cache_key]
            
            # Run simulation
            sim = BarotraumaSimulation(scenario)
            time_array, altitude_array, cabin_pressure_points, P_cabin_func, altitude_func = \
                simulate_flight_profile(
                    scenario.get('initial_altitude_ft', 0),
                    scenario.get('final_altitude_ft', 35000),
                    scenario.get('climb_rate_ft_min', 2000),
                    scenario.get('descent_rate_ft_min', 1500),
                    scenario.get('cruise_duration_min', 120)
                )
            
            result = sim.simulate_flight(time_array, P_cabin_func, altitude_func)
            
            if result is not None:
                time_array, P_ME_history, V_ME_history, delta_P, risk, risk_score = result
                
                # Create simulation result object
                sim_result = SimulationResult(
                    pressure_history=P_ME_history,
                    volume_history=V_ME_history,
                    time=time_array,
                    gas_exchange_rates=sim.k_MEM,
                    risk_score=risk_score,
                    risk_category=risk
                )
                
                # Validate and cache if valid
                if sim_result.validate():
                    self.simulation_cache[cache_key] = sim_result
                    return sim_result
                else:
                    self.logger.warning("Simulation results failed validation")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Simulation error: {str(e)}")
            return None
    
    def _extract_features(self, scenario: Dict) -> Optional[np.ndarray]:
        """Extract features for ML model from scenario and simulation results."""
        try:
            sim_result = self._simulate_scenario(scenario)
            if sim_result is None:
                return None
            
            # Calculate statistical features from simulation results
            pressure_stats = {
                'max': np.max(np.abs(sim_result.pressure_history)),
                'mean': np.mean(sim_result.pressure_history),
                'std': np.std(sim_result.pressure_history),
                'rate': np.max(np.abs(np.gradient(sim_result.pressure_history, sim_result.time)))
            }
            
            volume_stats = {
                'max': np.max(sim_result.volume_history),
                'min': np.min(sim_result.volume_history),
                'change': np.max(sim_result.volume_history) - np.min(sim_result.volume_history),
                'rate': np.max(np.abs(np.gradient(sim_result.volume_history, sim_result.time)))
            }
            
            # Combine features
            features = [
                scenario['et_dysfunction'],
                pressure_stats['max'],
                pressure_stats['mean'],
                pressure_stats['std'],
                pressure_stats['rate'],
                volume_stats['max'],
                volume_stats['min'],
                volume_stats['change'],
                volume_stats['rate'],
                *[rate for rate in sim_result.gas_exchange_rates.values()]
            ]
            
            return np.array(features)
            
        except Exception as e:
            self.logger.error(f"Feature extraction error: {str(e)}")
            return None
    
    def fit(self, scenarios: List[Dict], labels: np.ndarray, 
            validation_data: Optional[Tuple] = None) -> Dict:
        """Train the integrated model."""
        try:
            # Extract features
            features = []
            valid_indices = []
            
            for i, scenario in enumerate(scenarios):
                feature_vector = self._extract_features(scenario)
                if feature_vector is not None:
                    features.append(feature_vector)
                    valid_indices.append(i)
            
            if not features:
                raise ValueError("No valid features extracted")
            
            X = np.array(features)
            y = labels[valid_indices]
            
            # Scale features
            X = self.scaler.fit_transform(X)
            
            # Train and calibrate RF
            self.calibrated_rf = CalibratedClassifierCV(
                self.rf_classifier, 
                cv=5, 
                method='sigmoid'
            )
            self.calibrated_rf.fit(X, y)
            
            # Train and calibrate GB
            self.calibrated_gb = CalibratedClassifierCV(
                self.gb_classifier,
                cv=5,
                method='sigmoid'
            )
            self.calibrated_gb.fit(X, y)
            
            # Cross-validation
            cv_results = cross_validate(
                self.rf_classifier,
                X,
                y,
                cv=5,
                scoring=['roc_auc', 'accuracy', 'precision', 'recall']
            )
            
            # Validation metrics
            validation_metrics = {}
            if validation_data is not None:
                val_scenarios, val_labels = validation_data
                val_features = []
                val_valid_indices = []
                
                for i, scenario in enumerate(val_scenarios):
                    feature_vector = self._extract_features(scenario)
                    if feature_vector is not None:
                        val_features.append(feature_vector)
                        val_valid_indices.append(i)
                
                if val_features:
                    val_features = np.array(val_features)
                    val_features = self.scaler.transform(val_features)
                    val_labels = val_labels[val_valid_indices]
                    
                    rf_val_pred = self.calibrated_rf.predict_proba(val_features)[:, 1]
                    gb_val_pred = self.calibrated_gb.predict_proba(val_features)[:, 1]
                    
                    validation_metrics = {
                        'rf_val_auc': roc_auc_score(val_labels, rf_val_pred),
                        'gb_val_auc': roc_auc_score(val_labels, gb_val_pred)
                    }
            
            return {
                'cv_results': cv_results,
                'validation_metrics': validation_metrics,
                'n_samples': len(X)
            }
            
        except Exception as e:
            self.logger.error(f"Training error: {str(e)}")
            return {'error': str(e)}
    
    def predict(self, scenarios: List[Dict], 
                return_uncertainty: bool = False) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Make predictions using the integrated model."""
        try:
            if not self.calibrated_rf or not self.calibrated_gb:
                raise ValueError("Model not trained")
            
            # Get physical and ML predictions
            physical_predictions = []
            physical_uncertainties = []
            features = []
            
            for scenario in scenarios:
                # Run physical simulation
                sim_result = self._simulate_scenario(scenario)
                if sim_result is None:
                    continue
                
                physical_predictions.append(sim_result.risk_score)
                physical_uncertainties.append(0.2)  # Base uncertainty
                
                # Extract features for ML
                feature_vector = self._extract_features(scenario)
                if feature_vector is not None:
                    features.append(feature_vector)
            
            if not features:
                raise ValueError("No valid predictions")
            
            # ML predictions
            X = np.array(features)
            X = self.scaler.transform(X)
            
            rf_pred = self.calibrated_rf.predict_proba(X)[:, 1]
            gb_pred = self.calibrated_gb.predict_proba(X)[:, 1]
            
            # Combine predictions
            ml_predictions = 0.5 * (rf_pred + gb_pred)
            final_predictions = (self.physical_weight * np.array(physical_predictions) + 
                               self.ml_weight * ml_predictions)
            
            if return_uncertainty:
                # Calculate uncertainties
                model_disagreement = np.abs(rf_pred - gb_pred)
                physical_ml_disagreement = np.abs(np.array(physical_predictions) - ml_predictions)
                
                uncertainties = np.sqrt(
                    0.5 * model_disagreement**2 + 
                    0.3 * physical_ml_disagreement**2 +
                    0.2 * np.array(physical_uncertainties)**2
                )
                return final_predictions, uncertainties
            
            return final_predictions, None
            
        except Exception as e:
            self.logger.error(f"Prediction error: {str(e)}")
            return np.array([]), None
    
    def save_model(self, path: Path):
        """Save the integrated model."""
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'rf_model': self.calibrated_rf,
            'gb_model': self.calibrated_gb,
            'scaler': self.scaler,
            'physical_weight': self.physical_weight
        }, path)
    
    def load_model(self, path: Path):
        """Load the integrated model."""
        model_data = joblib.load(path)
        self.calibrated_rf = model_data['rf_model']
        self.calibrated_gb = model_data['gb_model']
        self.scaler = model_data['scaler']
        self.physical_weight = model_data['physical_weight']
        self.ml_weight = 1 - self.physical_weight
    
    def _validate_physiological_constraints(self, sim_result: SimulationResult) -> Dict[str, bool]:
        """
        Validate that simulation results meet physiological constraints.
        
        Args:
            sim_result: SimulationResult object
            
        Returns:
            Dictionary of validation results
        """
        constraints = {
            'pressure_valid': True,
            'volume_valid': True,
            'gas_exchange_valid': True,
            'rate_valid': True,
            'messages': []
        }
        
        # Pressure constraints
        max_pressure = np.max(np.abs(sim_result.pressure_history))
        if max_pressure > 200:  # mmHg
            constraints['pressure_valid'] = False
            constraints['messages'].append(
                f"Maximum pressure {max_pressure:.1f} mmHg exceeds physiological limit"
            )
        
        # Volume constraints
        volume_change = np.max(sim_result.volume_history) - np.min(sim_result.volume_history)
        if volume_change > 3e-3:  # L
            constraints['volume_valid'] = False
            constraints['messages'].append(
                f"Volume change {volume_change*1000:.2f} mL exceeds physiological limit"
            )
        
        # Rate constraints
        pressure_rate = np.max(np.abs(np.gradient(sim_result.pressure_history, sim_result.time)))
        if pressure_rate > 50:  # mmHg/s
            constraints['rate_valid'] = False
            constraints['messages'].append(
                f"Pressure rate {pressure_rate:.1f} mmHg/s exceeds physiological limit"
            )
        
        # Gas exchange constraints
        for gas, rate in sim_result.gas_exchange_rates.items():
            if rate > 1e-3:  # mol/s
                constraints['gas_exchange_valid'] = False
                constraints['messages'].append(
                    f"Gas exchange rate for {gas} ({rate:.6f} mol/s) exceeds physiological limit"
                )
        
        return constraints
    
    def analyze_feature_importance(self) -> Dict[str, float]:
        """
        Analyze feature importance from both physical and ML perspectives.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.calibrated_rf is None:
            raise ValueError("Model must be trained before analyzing feature importance")
        
        # Get feature names
        feature_names = [
            'et_dysfunction',
            'pressure_max',
            'pressure_mean',
            'pressure_std',
            'pressure_rate',
            'volume_max',
            'volume_min',
            'volume_change',
            'volume_rate',
            'O2_exchange',
            'CO2_exchange',
            'N2_exchange',
            'H2O_exchange'
        ]
        
        # Get importance scores from RF
        rf_importance = self.rf_classifier.feature_importances_
        
        # Get importance scores from GB
        gb_importance = self.gb_classifier.feature_importances_
        
        # Combine importance scores with weights
        combined_importance = (
            0.6 * rf_importance +
            0.4 * gb_importance
        )
        
        # Normalize importance scores
        normalized_importance = combined_importance / np.sum(combined_importance)
        
        return dict(zip(feature_names, normalized_importance))
    
    def analyze_prediction_confidence(self, scenario: Dict) -> Dict:
        """
        Analyze confidence in prediction for a given scenario.
        
        Args:
            scenario: Dictionary containing scenario parameters
            
        Returns:
            Dictionary containing confidence analysis
        """
        # Run simulation
        sim_result = self._simulate_scenario(scenario)
        if sim_result is None:
            return {'confidence': 0.0, 'reason': 'Simulation failed'}
        
        # Validate physiological constraints
        constraints = self._validate_physiological_constraints(sim_result)
        if not all(constraints[k] for k in ['pressure_valid', 'volume_valid', 
                                          'gas_exchange_valid', 'rate_valid']):
            return {
                'confidence': 0.2,
                'reason': 'Physiological constraints violated',
                'messages': constraints['messages']
            }
        
        # Get ML predictions and uncertainty
        features = self._extract_features(scenario)
        if features is None:
            return {'confidence': 0.0, 'reason': 'Feature extraction failed'}
        
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        rf_pred = self.calibrated_rf.predict_proba(features_scaled)[0, 1]
        gb_pred = self.calibrated_gb.predict_proba(features_scaled)[0, 1]
        
        # Calculate prediction agreement
        pred_diff = abs(rf_pred - gb_pred)
        ml_confidence = 1 - pred_diff
        
        # Calculate physical confidence based on risk score
        phys_confidence = 1 - abs(0.5 - sim_result.risk_score)
        
        # Combine confidences
        combined_confidence = (
            self.physical_weight * phys_confidence +
            self.ml_weight * ml_confidence
        )
        
        return {
            'confidence': combined_confidence,
            'physical_confidence': phys_confidence,
            'ml_confidence': ml_confidence,
            'model_agreement': 1 - pred_diff,
            'risk_score': sim_result.risk_score,
            'risk_category': sim_result.risk_category
        }
    
    def get_feature_ranges(self) -> Dict[str, Tuple[float, float]]:
        """
        Get physiologically valid ranges for features.
        
        Returns:
            Dictionary mapping feature names to (min, max) tuples
        """
        return {
            'et_dysfunction': (0, 1),
            'pressure_max': (0, 200),  # mmHg
            'pressure_mean': (-50, 50),  # mmHg
            'pressure_std': (0, 50),  # mmHg
            'pressure_rate': (0, 50),  # mmHg/s
            'volume_max': (0.5e-3, 20e-3),  # L
            'volume_min': (0.5e-3, 20e-3),  # L
            'volume_change': (0, 3e-3),  # L
            'volume_rate': (0, 0.1e-3),  # L/s
            'O2_exchange': (0, 1e-3),  # mol/s
            'CO2_exchange': (0, 1e-3),  # mol/s
            'N2_exchange': (0, 1e-4),  # mol/s
            'H2O_exchange': (0, 1e-3)  # mol/s
        }
    
    def validate_scenario(self, scenario: Dict) -> Dict:
        """
        Validate a scenario against physiological constraints.
        
        Args:
            scenario: Dictionary containing scenario parameters
            
        Returns:
            Dictionary containing validation results
        """
        validation = {
            'valid': True,
            'messages': []
        }
        
        # Validate ET dysfunction
        if not 0 <= scenario.get('et_dysfunction', 0) <= 1:
            validation['valid'] = False
            validation['messages'].append("ET dysfunction must be between 0 and 1")
        
        # Validate volumes
        if not 0.5e-3 <= scenario.get('V_tym', 1.0e-3) <= 2.0e-3:
            validation['valid'] = False
            validation['messages'].append("Tympanic volume outside physiological range")
        
        if not 3.0e-3 <= scenario.get('V_mas', 7.75e-3) <= 12.0e-3:
            validation['valid'] = False
            validation['messages'].append("Mastoid volume outside physiological range")
        
        # Validate flight parameters
        if scenario.get('climb_rate_ft_min', 0) > 3000:
            validation['valid'] = False
            validation['messages'].append("Climb rate exceeds typical limit")
        
        if scenario.get('descent_rate_ft_min', 0) > 3000:
            validation['valid'] = False
            validation['messages'].append("Descent rate exceeds typical limit")
        
        # Validate gas exchange parameters
        k_MEM = scenario.get('k_MEM', {})
        for gas, rate in k_MEM.items():
            if rate > 1e-3:
                validation['valid'] = False
                validation['messages'].append(f"Gas exchange rate for {gas} exceeds physiological limit")
        
        return validation
    
    def _calculate_cumulative_exposure(self, time: np.ndarray, 
                                     pressure: np.ndarray) -> float:
        """Calculate cumulative pressure exposure."""
        return trapezoid(np.abs(pressure), time)