# Backend Design Document

## Transport Delay Prediction System - Backend Architecture

---

## 1. Executive Summary

This document outlines the backend architecture for the Transport Delay Prediction web application. The backend is built using **FastAPI** (Python) and provides a RESTful API for delay prediction using a pre-trained machine learning model.

**Key Design Principles:**
- Simplicity and maintainability
- Clear separation of concerns
- Production-ready error handling
- Extensible architecture

---

## 2. Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Framework** | FastAPI | High performance, automatic API documentation, modern async support |
| **Language** | Python 3.9+ | ML ecosystem compatibility, readable codebase |
| **ML Libraries** | scikit-learn, pandas, numpy | Standard ML stack, model compatibility |
| **Validation** | Pydantic | Built-in with FastAPI, strong type checking |
| **Server** | Uvicorn | ASGI server, production-ready |
| **CORS** | FastAPI CORS Middleware | Enable cross-origin requests from frontend |

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────┐
│   Frontend  │
│  (Browser)  │
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────────────────────────┐
│      FastAPI Application        │
│  ┌───────────────────────────┐  │
│  │   API Layer (Routes)      │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │   Service Layer           │  │
│  │  (Business Logic)         │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │   ML Model Layer          │  │
│  │  (Prediction Engine)      │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 3.2 Directory Structure

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── prediction.py   # Prediction endpoints
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic models (request/response)
│   │   └── ml_model.py         # ML model wrapper class
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── prediction_service.py  # Business logic
│   │
│   └── utils/
│       ├── __init__.py
│       └── validators.py       # Custom validation functions
│
├── ml_models/
│   ├── trained_model.pkl       # Serialized ML model
│   └── feature_config.json     # Feature metadata
│
├── tests/
│   ├── __init__.py
│   ├── test_prediction.py
│   └── test_validation.py
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. Core Components

### 4.1 Application Entry Point (`main.py`)

**Purpose:** Initialize FastAPI application, configure middleware, and register routes.

**Key Responsibilities:**
- Application initialization
- CORS configuration
- Route registration
- Global exception handling
- Health check endpoint

**Implementation Highlights:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Transport Delay Prediction API",
    description="ML-powered delay prediction service",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_methods=["*"],
    allow_headers=["*"]
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

### 4.2 Data Models (`schemas.py`)

**Purpose:** Define request and response data structures using Pydantic.

**Key Models:**

#### PredictionRequest
```python
class PredictionRequest(BaseModel):
    route_id: int = Field(..., ge=1, description="Route identifier")
    weather: str = Field(..., description="Weather condition")
    passenger_count: int = Field(..., ge=0, le=500)
    time_of_day: int = Field(..., ge=0, le=23, description="Hour (0-23)")
    is_weekend: int = Field(..., ge=0, le=1, description="0=weekday, 1=weekend")
    
    @validator('weather')
    def validate_weather(cls, v):
        allowed = ['sunny', 'cloudy', 'rainy', 'snowy']
        if v.lower() not in allowed:
            raise ValueError(f"Weather must be one of: {allowed}")
        return v.lower()
```

#### PredictionResponse
```python
class PredictionResponse(BaseModel):
    predicted_delay: float = Field(..., description="Delay in minutes")
    model_name: str = Field(default="Random Forest Regressor")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

#### FeatureImportanceResponse
```python
class FeatureImportance(BaseModel):
    feature_name: str
    importance_score: float

class FeatureImportanceResponse(BaseModel):
    importances: List[FeatureImportance]
    explanation: str
```

---

### 4.3 ML Model Wrapper (`ml_model.py`)

**Purpose:** Encapsulate model loading, prediction logic, and feature importance extraction.

**Design Pattern:** Singleton pattern to load model once at startup.

**Key Methods:**

```python
class MLModelWrapper:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """Load the trained model from disk"""
        model_path = Path("ml_models/trained_model.pkl")
        self.model = joblib.load(model_path)
        self.feature_names = [...]  # Load feature configuration
    
    def predict(self, features: dict) -> float:
        """Generate delay prediction"""
        # Convert dict to DataFrame
        # Apply preprocessing
        # Return prediction
    
    def get_feature_importance(self) -> List[dict]:
        """Extract feature importance from model"""
        # Return sorted list of features with importance scores
```

**Error Handling:**
- Model file not found
- Corrupted model file
- Prediction errors
- Feature mismatch

---

### 4.4 Prediction Service (`prediction_service.py`)

**Purpose:** Business logic layer between API routes and ML model.

**Key Responsibilities:**
- Coordinate model prediction
- Transform input data
- Generate explanations
- Log predictions (optional)

**Implementation:**
```python
class PredictionService:
    def __init__(self):
        self.model = MLModelWrapper()
    
    async def predict_delay(
        self, 
        request: PredictionRequest
    ) -> PredictionResponse:
        """
        Main prediction workflow:
        1. Validate input
        2. Prepare features
        3. Get prediction
        4. Format response
        """
        features = self._prepare_features(request)
        delay = self.model.predict(features)
        
        return PredictionResponse(
            predicted_delay=round(delay, 2),
            model_name="Random Forest Regressor"
        )
    
    def _prepare_features(self, request: PredictionRequest) -> dict:
        """Transform request into model-ready features"""
        # Handle categorical encoding
        # Apply feature scaling if needed
        return features
```

---

### 4.5 API Routes (`prediction.py`)

**Purpose:** Define HTTP endpoints and handle request/response.

**Endpoints:**

#### POST `/api/v1/predict`
```python
@router.post("/predict", response_model=PredictionResponse)
async def predict_delay(request: PredictionRequest):
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
        result = await service.predict_delay(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Prediction failed")
```

#### GET `/api/v1/feature-importance`
```python
@router.get("/feature-importance", response_model=FeatureImportanceResponse)
async def get_feature_importance():
    """
    Retrieve feature importance from the trained model.
    
    Returns:
        Sorted list of features with importance scores
    """
    service = PredictionService()
    importances = service.model.get_feature_importance()
    
    return FeatureImportanceResponse(
        importances=importances,
        explanation="Features ranked by impact on delay prediction"
    )
```

#### GET `/api/v1/health`
```python
@router.get("/health")
async def health_check():
    """
    Check API and model health status.
    
    Returns:
        Status indicators for system components
    """
    return {
        "status": "healthy",
        "model_loaded": MLModelWrapper()._instance is not None,
        "timestamp": datetime.utcnow()
    }
```

---

## 5. Configuration Management

### 5.1 Configuration File (`config.py`)

**Purpose:** Centralize application settings and environment variables.

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Transport Delay Prediction API"
    VERSION: str = "1.0.0"
    
    # Model Settings
    MODEL_PATH: str = "ml_models/trained_model.pkl"
    FEATURE_CONFIG_PATH: str = "ml_models/feature_config.json"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS Settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 5.2 Environment Variables (`.env.example`)

```env
# API Configuration
API_V1_PREFIX=/api/v1
DEBUG=False

# Model Configuration
MODEL_PATH=ml_models/trained_model.pkl

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 6. Error Handling Strategy

### 6.1 Exception Hierarchy

```python
class PredictionError(Exception):
    """Base exception for prediction errors"""
    pass

class ModelNotFoundError(PredictionError):
    """Model file not found"""
    pass

class InvalidFeatureError(PredictionError):
    """Invalid feature values"""
    pass
```

### 6.2 Global Exception Handler

```python
@app.exception_handler(PredictionError)
async def prediction_exception_handler(request: Request, exc: PredictionError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Prediction Error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

---

## 7. Data Validation

### 7.1 Input Validation Rules

| Field | Validation Rules |
|-------|-----------------|
| `route_id` | Integer, >= 1 |
| `weather` | Enum: [sunny, cloudy, rainy, snowy] |
| `passenger_count` | Integer, 0-500 |
| `time_of_day` | Integer, 0-23 |
| `is_weekend` | Binary, 0 or 1 |

### 7.2 Custom Validators

```python
def validate_business_hours(time_of_day: int, is_weekend: int):
    """Validate reasonable transport operating hours"""
    if is_weekend == 0 and (time_of_day < 5 or time_of_day > 23):
        raise ValueError("Unusual operating hours for weekday")
```

---

## 8. Performance Considerations

### 8.1 Optimization Strategies

- **Model Caching:** Load model once at startup using Singleton pattern
- **Async Operations:** Use async/await for non-blocking I/O
- **Response Compression:** Enable gzip compression middleware
- **Connection Pooling:** Reuse connections (if using database in future)

### 8.2 Expected Performance

| Metric | Target | Typical |
|--------|--------|---------|
| Prediction latency | < 2s | ~100-300ms |
| Throughput | 100 req/s | 50-150 req/s |
| Memory usage | < 500MB | ~200-300MB |

---

## 9. Security Measures

### 9.1 Input Sanitization

- Pydantic automatic validation
- SQL injection prevention (for future database integration)
- XSS protection through JSON serialization

### 9.2 Rate Limiting (Future Enhancement)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/predict")
@limiter.limit("10/minute")
async def predict_delay(request: Request, data: PredictionRequest):
    ...
```

---

## 10. Testing Strategy

### 10.1 Unit Tests

```python
# tests/test_prediction.py
def test_valid_prediction():
    request = PredictionRequest(
        route_id=3,
        weather="cloudy",
        passenger_count=120,
        time_of_day=15,
        is_weekend=0
    )
    response = predict_delay(request)
    assert response.predicted_delay > 0

def test_invalid_weather():
    with pytest.raises(ValueError):
        PredictionRequest(
            route_id=3,
            weather="foggy",  # Invalid
            passenger_count=120,
            time_of_day=15,
            is_weekend=0
        )
```

### 10.2 Integration Tests

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_predict_endpoint():
    response = client.post("/api/v1/predict", json={
        "route_id": 3,
        "weather": "cloudy",
        "passenger_count": 120,
        "time_of_day": 15,
        "is_weekend": 0
    })
    assert response.status_code == 200
    assert "predicted_delay" in response.json()
```

---

## 11. Deployment

### 11.1 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 11.2 Production Deployment

```bash
# Run with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 11.3 Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 12. API Documentation

### 12.1 Automatic Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`

### 12.2 Example API Calls

**Predict Delay:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "route_id": 3,
    "weather": "cloudy",
    "passenger_count": 120,
    "time_of_day": 15,
    "is_weekend": 0
  }'
```

**Response:**
```json
{
  "predicted_delay": 18.5,
  "model_name": "Random Forest Regressor",
  "timestamp": "2025-12-19T10:30:00Z"
}
```

---

## 13. Monitoring & Logging

### 13.1 Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 13.2 Key Metrics to Log

- Request timestamps
- Prediction latency
- Input features (for debugging)
- Error rates
- Model version

---

## 14. Future Enhancements

### Phase 2 Features

1. **Database Integration**
   - Store prediction history
   - User analytics
   - PostgreSQL/MongoDB

2. **Authentication**
   - JWT tokens
   - API keys
   - Rate limiting per user

3. **Model Versioning**
   - Multiple model support
   - A/B testing
   - Model registry

4. **Advanced Features**
   - Batch predictions
   - Real-time traffic integration
   - WebSocket support for live updates

---

## 15. Dependencies

### 15.1 Core Requirements (`requirements.txt`)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
joblib==1.3.2
python-multipart==0.0.6
```

### 15.2 Development Dependencies

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
black==23.11.0
flake8==6.1.0
mypy==1.7.1
```

---

## 16. Conclusion

This backend design provides a **robust, scalable, and maintainable** foundation for the Transport Delay Prediction system. The architecture emphasizes:

- Clear separation of concerns
- Type safety through Pydantic
- Comprehensive error handling
- Production-ready performance
- Easy extensibility for future features

The FastAPI framework ensures automatic API documentation, high performance, and modern Python features, making this backend both developer-friendly and production-ready.

---

**Document Version:** 1.0  
**Last Updated:** December 2025  
**Author:** Backend Development Team