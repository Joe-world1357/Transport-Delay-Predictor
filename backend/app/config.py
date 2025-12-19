"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Transport Delay Prediction API"
    VERSION: str = "1.0.0"
    
    # Model Settings
    MODEL_PATH: str = "ml_models/trained_model.pkl"
    FEATURE_CONFIG_PATH: str = "ml_models/feature_config.json"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    DEBUG: bool = False
    
    # CORS Settings
    # For development, use ["*"] to allow all origins
    # For production, specify exact origins
    # Can be set via environment variable as comma-separated string
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://localhost:3000,http://localhost:5173,http://127.0.0.1:8000"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated string to list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        return self.ALLOWED_ORIGINS if isinstance(self.ALLOWED_ORIGINS, list) else []
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

