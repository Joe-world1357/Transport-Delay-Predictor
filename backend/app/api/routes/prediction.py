"""
Prediction API routes
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Query
from typing import Dict, Optional
import logging
import pandas as pd
from pathlib import Path

from app.models.schemas import (
    PredictionRequest,
    PredictionResponse,
    FeatureImportanceResponse,
    FeatureImportance,
    ErrorResponse
)
from app.services.prediction_service import PredictionService
from app.models.ml_model import MLModelWrapper

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Server error"}
    }
)
async def predict_delay(
    request: PredictionRequest,
    model: Optional[str] = Query(None, description="Model name to use (gradient_boosting, random_forest, linear_regression, knn)")
) -> PredictionResponse:
    """
    Predict transport delay based on input features.
    
    Args:
        request: Validated prediction request
        
    Returns:
        PredictionResponse with delay prediction
        
    Raises:
        HTTPException: 400 for validation errors
        HTTPException: 500 for server errors
    """
    try:
        service = PredictionService()
        result = await service.predict_delay(request, model_name=model)
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation Error",
                "message": str(e),
                "details": {}
            }
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        error_detail = {
            "error": "Prediction Failed",
            "message": str(e) if str(e) else "An error occurred while making the prediction. Please try again.",
            "details": {}
        }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get(
    "/feature-importance",
    response_model=FeatureImportanceResponse,
    status_code=status.HTTP_200_OK
)
async def get_feature_importance() -> FeatureImportanceResponse:
    """
    Retrieve feature importance from the trained model.
    
    Returns:
        FeatureImportanceResponse with sorted list of features and importance scores
    """
    try:
        service = PredictionService()
        importances = service.get_feature_importance()
        
        # Convert to FeatureImportance objects
        feature_importances = [
            FeatureImportance(name=item["name"], importance=item["importance"])
            for item in importances
        ]
        
        return FeatureImportanceResponse(
            importances=feature_importances,
            explanation="Features ranked by impact on delay prediction"
        )
        
    except Exception as e:
        logger.error(f"Error getting feature importance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Feature Importance Error",
                "message": str(e)
            }
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK
)
async def health_check() -> Dict:
    """
    Check API and model health status.
    
    Returns:
        Status indicators for system components
    """
    try:
        model = MLModelWrapper()
        model_loaded = model.is_loaded()
        
        return {
            "status": "healthy",
            "model_loaded": model_loaded,
            "message": "Service is operational" if model_loaded else "Service running in mock mode"
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "degraded",
            "model_loaded": False,
            "message": f"Service error: {str(e)}"
        }

