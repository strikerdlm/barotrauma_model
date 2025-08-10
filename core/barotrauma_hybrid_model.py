"""
Hybrid model for barotrauma prediction combining physics-based simulation with machine learning.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

class BarotraumaHybridModel:
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def _extract_features(self, scenarios):
        """Extract relevant features from scenarios."""
        features = []
        for scenario in scenarios:
            features.append([
                scenario['final_altitude_ft'],
                scenario['climb_rate_ft_min'],
                scenario['descent_rate_ft_min'],
                scenario['cruise_duration_min'],
                scenario['et_dysfunction'],
                scenario['inflammation']
            ])
        return np.array(features)
    
    def fit(self, train_scenarios, train_outcomes, validation_data=None):
        """Train the hybrid model."""
        # Extract features
        X_train = self._extract_features(train_scenarios)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train classifier
        self.classifier.fit(X_train_scaled, train_outcomes)
        
        # Validate if validation data is provided
        if validation_data:
            val_scenarios, val_outcomes = validation_data
            X_val = self._extract_features(val_scenarios)
            X_val_scaled = self.scaler.transform(X_val)
            val_score = self.classifier.score(X_val_scaled, val_outcomes)
            print(f"Validation accuracy: {val_score:.2f}")
    
    def predict(self, scenarios, return_uncertainty=False):
        """Make predictions with uncertainty estimates."""
        X = self._extract_features(scenarios)
        X_scaled = self.scaler.transform(X)
        
        # Get predictions
        predictions = self.classifier.predict_proba(X_scaled)[:, 1]  # Probability of high risk
        
        if return_uncertainty:
            # Calculate uncertainty using prediction variance across trees
            predictions_all_trees = np.array([tree.predict_proba(X_scaled)[:, 1] 
                                           for tree in self.classifier.estimators_])
            uncertainties = np.std(predictions_all_trees, axis=0)
            return predictions, uncertainties
        
        return predictions
    
    def save_model(self, path):
        """Save the model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'classifier': self.classifier,
            'scaler': self.scaler
        }, path + '.joblib')