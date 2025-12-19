"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request model for delay prediction"""
    route_id: int = Field(..., ge=1, le=10, description="Route identifier (1-10)")
    weather: str = Field(..., description="Weather condition")
    passenger_count: int = Field(..., ge=0, le=500, description="Number of passengers")
    time_of_day: int = Field(..., ge=0, le=3, description="Time period: 0=Morning, 1=Afternoon, 2=Evening, 3=Night")
    is_weekend: int = Field(..., ge=0, le=1, description="0=weekday, 1=weekend")
    
    @validator('weather')
    def validate_weather(cls, v):
        """Validate weather condition"""
        allowed = ['clear', 'cloudy', 'rainy', 'snowy', 'sunny']
        weather_lower = v.lower()
        if weather_lower not in allowed:
            raise ValueError(f"Weather must be one of: {allowed}")
        # Normalize to standard values
        if weather_lower == 'sunny':
            return 'clear'
        return weather_lower
    
    class Config:
        json_schema_extra = {
            "example": {
                "route_id": 3,
                "weather": "cloudy",
                "passenger_count": 120,
                "time_of_day": 1,
                "is_weekend": 0
            }
        }


class PredictionResponse(BaseModel):
    """Response model for delay prediction"""
    predicted_delay: float = Field(..., description="Predicted delay in minutes")
    model_name: str = Field(default="Random Forest Regressor", description="Name of the ML model used")
    mae: Optional[float] = Field(default=None, description="Mean Absolute Error of the model")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Prediction timestamp")
    feature_importance: Optional[List[dict]] = Field(
        default=None, 
        description="Top features contributing to prediction"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_delay": 18.5,
                "model_name": "Random Forest Regressor",
                "mae": 3.2,
                "timestamp": "2024-12-19T10:30:00Z",
                "feature_importance": [
                    {"name": "weather", "importance": 0.45},
                    {"name": "time_of_day", "importance": 0.30},
                    {"name": "passenger_count", "importance": 0.25}
                ]
            }
        }


class FeatureImportance(BaseModel):
    """Feature importance data model"""
    name: str = Field(..., description="Feature name")
    importance: float = Field(..., description="Importance score (0-1)")


class FeatureImportanceResponse(BaseModel):
    """Response model for feature importance"""
    importances: List[FeatureImportance] = Field(..., description="List of features with importance scores")
    explanation: str = Field(
        default="Features ranked by impact on delay prediction",
        description="Explanation of feature importance"
    )


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

