"""
Prediction Service - Business logic layer
"""
from typing import Dict
import logging

from app.models.ml_model import MLModelWrapper
from app.models.schemas import PredictionRequest, PredictionResponse
from app.utils.validators import validate_business_hours, validate_route_operating_hours

logger = logging.getLogger(__name__)


class PredictionService:
    """Service layer for prediction business logic"""
    
    def __init__(self):
        """Initialize service with ML model"""
        self.model = MLModelWrapper()
    
    async def predict_delay(self, request: PredictionRequest, model_name: str = None) -> PredictionResponse:
        """
        Main prediction workflow
        
        Args:
            request: Validated prediction request
            
        Returns:
            PredictionResponse with delay prediction and metadata
        """
        try:
            # Optional: Validate business rules
            validate_business_hours(request.time_of_day, request.is_weekend)
            validate_route_operating_hours(request.route_id, request.time_of_day)
            
            # Prepare features from request
            features = self._prepare_features(request)
            
            # Get prediction from model (use specified model if provided)
            if model_name:
                predicted_delay = self.model.predict_with_model(features, model_name)
            else:
                predicted_delay = self.model.predict(features)
            
            # Get feature importance if available
            feature_importance = None
            try:
                importances = self.model.get_feature_importance()
                if importances:
                    feature_importance = importances
            except Exception as e:
                logger.warning(f"Could not get feature importance: {str(e)}")
            
            # Get model MAE (if available from model metadata)
            mae = 3.2  # Default MAE, can be loaded from model metadata
            
            # Get model name for display
            model_display_names = {
                'gradient_boosting': 'Gradient Boosting Regressor',
                'random_forest': 'Random Forest Regressor',
                'linear_regression': 'Linear Regression',
                'knn': 'k-Nearest Neighbors Regressor'
            }
            
            model_display = model_display_names.get(model_name, 'Random Forest Regressor') if model_name else 'Random Forest Regressor'
            
            # Build response
            response = PredictionResponse(
                predicted_delay=predicted_delay,
                model_name=model_display,
                mae=mae,
                feature_importance=feature_importance
            )
            
            logger.info(f"Prediction made: {predicted_delay} minutes delay")
            
            return response
            
        except Exception as e:
            logger.error(f"Prediction service error: {str(e)}")
            raise
    
    def _prepare_features(self, request: PredictionRequest) -> Dict:
        """
        Transform request into model-ready features
        
        Args:
            request: PredictionRequest object
            
        Returns:
            Dictionary of features
        """
        return {
            'route_id': request.route_id,
            'weather': request.weather,
            'passenger_count': request.passenger_count,
            'time_of_day': request.time_of_day,
            'is_weekend': request.is_weekend
        }
    
    def get_feature_importance(self) -> list:
        """
        Get feature importance from model
        
        Returns:
            List of feature importance dictionaries
        """
        return self.model.get_feature_importance()

