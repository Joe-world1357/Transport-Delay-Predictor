"""
ML Model Wrapper - Singleton pattern for model loading and prediction
"""
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MLModelWrapper:
    """
    Singleton wrapper for ML model.
    Loads model once at startup and provides prediction interface.
    """
    _instance = None
    _model = None
    _feature_names = None
    _model_loaded = False
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """Load the trained model from disk"""
        try:
            model_path = Path(__file__).parent.parent.parent / "ml_models" / "trained_model.pkl"
            
            if not model_path.exists():
                logger.warning(f"Model file not found at {model_path}. Using mock model.")
                self._model_loaded = False
                self._feature_names = [
                    'route_id', 'weather_clear', 'weather_cloudy', 'weather_rainy', 'weather_snowy',
                    'passenger_count', 'time_of_day', 'is_weekend'
                ]
                return
            
            self._model = joblib.load(model_path)
            self._model_loaded = True
            
            # Load feature configuration if available
            feature_config_path = Path(__file__).parent.parent.parent / "ml_models" / "feature_config.json"
            if feature_config_path.exists():
                import json
                with open(feature_config_path, 'r') as f:
                    config = json.load(f)
                    self._feature_names = config.get('feature_names', [])
            else:
                # Default feature names if config not available
                self._feature_names = [
                    'route_id', 'weather_clear', 'weather_cloudy', 'weather_rainy', 'weather_snowy',
                    'passenger_count', 'time_of_day', 'is_weekend'
                ]
            
            logger.info("ML model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self._model_loaded = False
            self._feature_names = [
                'route_id', 'weather_clear', 'weather_cloudy', 'weather_rainy', 'weather_snowy',
                'passenger_count', 'time_of_day', 'is_weekend'
            ]
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._model_loaded
    
    def predict_with_model(self, features: Dict, model_name: str) -> float:
        """
        Predict using a specific model
        
        Args:
            features: Feature dictionary
            model_name: Name of model to use
            
        Returns:
            Predicted delay
        """
        model_path = Path(__file__).parent.parent.parent / "ml_pipeline" / "models" / f"{model_name}.pkl"
        
        if not model_path.exists():
            logger.warning(f"Model {model_name} not found, using default")
            return self.predict(features)
        
        try:
            specific_model = joblib.load(model_path)
            feature_vector = self._prepare_features(features)
            
            # Check if model needs scaling
            scaler_path = Path(__file__).parent.parent.parent / "ml_pipeline" / "models" / f"{model_name}_scaler.pkl"
            if scaler_path.exists() and model_name in ['linear_regression', 'knn']:
                scaler = joblib.load(scaler_path)
                feature_vector = scaler.transform(feature_vector)
            
            prediction = specific_model.predict(feature_vector)
            delay = max(0.0, float(prediction[0] if isinstance(prediction, np.ndarray) else prediction))
            return round(delay, 2)
        except Exception as e:
            logger.error(f"Error using model {model_name}: {str(e)}")
            return self.predict(features)
    
    def predict(self, features: Dict) -> float:
        """
        Generate delay prediction from features
        
        Args:
            features: Dictionary with feature values
            
        Returns:
            Predicted delay in minutes
        """
        if not self._model_loaded:
            # Mock prediction for development/testing
            return self._mock_predict(features)
        
        try:
            # Prepare features for model
            feature_vector = self._prepare_features(features)
            
            # Make prediction
            prediction = self._model.predict(feature_vector)
            
            # Ensure non-negative delay
            delay = max(0.0, float(prediction[0] if isinstance(prediction, np.ndarray) else prediction))
            
            return round(delay, 2)
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            # Fallback to mock prediction
            return self._mock_predict(features)
    
    def _prepare_features(self, features: Dict) -> pd.DataFrame:
        """
        Transform input features into model-ready format
        
        Args:
            features: Input feature dictionary
            
        Returns:
            DataFrame with features in correct order
        """
        # Create base feature vector in the exact order expected by model
        # Order: route_id, passenger_count, time_of_day, is_weekend, weather_clear, weather_cloudy, weather_rainy, weather_snowy
        feature_dict = {
            'route_id': features.get('route_id', 1),
            'passenger_count': features.get('passenger_count', 100),
            'time_of_day': features.get('time_of_day', 1),
            'is_weekend': features.get('is_weekend', 0),
            'weather_clear': 0,
            'weather_cloudy': 0,
            'weather_rainy': 0,
            'weather_snowy': 0
        }
        
        # One-hot encode weather
        weather = features.get('weather', 'clear').lower()
        if weather == 'clear':
            feature_dict['weather_clear'] = 1
        elif weather == 'cloudy':
            feature_dict['weather_cloudy'] = 1
        elif weather == 'rainy':
            feature_dict['weather_rainy'] = 1
        elif weather == 'snowy':
            feature_dict['weather_snowy'] = 1
        
        # Create DataFrame with correct column order matching model expectations
        if self._feature_names:
            # Use exact feature order from model
            df = pd.DataFrame([feature_dict])
            df = df.reindex(columns=self._feature_names, fill_value=0)
        else:
            # Fallback: create in expected order
            df = pd.DataFrame([[
                feature_dict['route_id'],
                feature_dict['passenger_count'],
                feature_dict['time_of_day'],
                feature_dict['is_weekend'],
                feature_dict['weather_clear'],
                feature_dict['weather_cloudy'],
                feature_dict['weather_rainy'],
                feature_dict['weather_snowy']
            ]], columns=[
                'route_id', 'passenger_count', 'time_of_day', 'is_weekend',
                'weather_clear', 'weather_cloudy', 'weather_rainy', 'weather_snowy'
            ])
        
        return df
    
    def _mock_predict(self, features: Dict) -> float:
        """
        Mock prediction for development/testing when model not available
        
        Args:
            features: Input feature dictionary
            
        Returns:
            Mock predicted delay
        """
        # Simple heuristic-based mock prediction
        base_delay = 10.0
        
        # Weather impact
        weather = features.get('weather', 'clear').lower()
        weather_multiplier = {
            'clear': 1.0,
            'cloudy': 1.2,
            'rainy': 1.5,
            'snowy': 2.0
        }
        base_delay *= weather_multiplier.get(weather, 1.0)
        
        # Passenger count impact
        passenger_count = features.get('passenger_count', 100)
        base_delay += (passenger_count / 100) * 2
        
        # Time of day impact
        time_of_day = features.get('time_of_day', 1)
        time_multiplier = {
            0: 1.1,  # Morning
            1: 1.3,  # Afternoon (rush hour)
            2: 1.2,  # Evening
            3: 0.9   # Night (less traffic)
        }
        base_delay *= time_multiplier.get(time_of_day, 1.0)
        
        # Weekend impact
        if features.get('is_weekend', 0) == 1:
            base_delay *= 0.8  # Less traffic on weekends
        
        # Route impact
        route_id = features.get('route_id', 1)
        base_delay += (route_id % 3) * 1.5
        
        return round(max(0.0, base_delay), 2)
    
    def get_feature_importance(self) -> List[Dict[str, float]]:
        """
        Extract feature importance from model
        
        Returns:
            List of dictionaries with feature names and importance scores
        """
        if not self._model_loaded or not hasattr(self._model, 'feature_importances_'):
            # Return mock feature importance
            return [
                {"name": "weather", "importance": 0.45},
                {"name": "time_of_day", "importance": 0.30},
                {"name": "passenger_count", "importance": 0.25}
            ]
        
        try:
            importances = self._model.feature_importances_
            feature_names = self._feature_names if self._feature_names else []
            
            # Map one-hot encoded weather features back to single feature
            importance_dict = {}
            weather_features = ['weather_clear', 'weather_cloudy', 'weather_rainy', 'weather_snowy']
            weather_importance = 0.0
            
            for i, feature_name in enumerate(feature_names):
                if i < len(importances):
                    if feature_name in weather_features:
                        weather_importance += importances[i]
                    else:
                        importance_dict[feature_name] = importances[i]
            
            # Add combined weather importance
            importance_dict['weather'] = weather_importance
            
            # Sort by importance
            sorted_features = sorted(
                importance_dict.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Return top features
            return [
                {"name": name, "importance": round(float(importance), 3)}
                for name, importance in sorted_features[:5]
            ]
            
        except Exception as e:
            logger.error(f"Error extracting feature importance: {str(e)}")
            return [
                {"name": "weather", "importance": 0.45},
                {"name": "time_of_day", "importance": 0.30},
                {"name": "passenger_count", "importance": 0.25}
            ]

