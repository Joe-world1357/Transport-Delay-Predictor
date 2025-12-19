# Transport Delay Prediction - Backend API

FastAPI-based backend for ML-powered transport delay prediction.

## Features

- **RESTful API** with automatic OpenAPI documentation
- **ML Model Integration** with singleton pattern for efficient loading
- **Input Validation** using Pydantic models
- **Error Handling** with comprehensive exception handling
- **CORS Support** for frontend integration
- **Mock Mode** for development without trained model

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

### 3. Add ML Model (Optional)

Place your trained model in `ml_models/`:
- `trained_model.pkl` - Serialized scikit-learn model
- `feature_config.json` - Feature configuration (optional)

**Note:** The API will run in mock mode if no model is provided.

### 4. Run the Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000

# Or use Python
python -m app.main
```

### 5. Access API Documentation

- **Swagger UI:** http://localhost:5000/docs
- **ReDoc:** http://localhost:5000/redoc
- **OpenAPI Schema:** http://localhost:5000/openapi.json

## API Endpoints

### POST `/api/v1/predict`

Predict transport delay based on input features.

**Request:**
```json
{
  "route_id": 3,
  "weather": "cloudy",
  "passenger_count": 120,
  "time_of_day": 1,
  "is_weekend": 0
}
```

**Response:**
```json
{
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
```

### GET `/api/v1/feature-importance`

Get feature importance from the trained model.

**Response:**
```json
{
  "importances": [
    {"name": "weather", "importance": 0.45},
    {"name": "time_of_day", "importance": 0.30},
    {"name": "passenger_count", "importance": 0.25}
  ],
  "explanation": "Features ranked by impact on delay prediction"
}
```

### GET `/api/v1/health`

Check API and model health status.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "message": "Service is operational"
}
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── api/
│   │   └── routes/
│   │       └── prediction.py
│   ├── models/
│   │   ├── schemas.py       # Pydantic models
│   │   └── ml_model.py      # ML model wrapper
│   ├── services/
│   │   └── prediction_service.py
│   └── utils/
│       └── validators.py
├── ml_models/               # Place trained models here
├── requirements.txt
└── README.md
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black app/
flake8 app/
```

## Mock Mode

If no trained model is available, the API runs in **mock mode** with heuristic-based predictions. This allows:
- Frontend development without backend model
- Testing API endpoints
- Demonstrating functionality

Mock predictions use simple heuristics based on:
- Weather conditions
- Passenger count
- Time of day
- Weekend status
- Route ID

## Production Deployment

### Using Uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5000 --workers 4
```

### Using Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
```

## Configuration

All settings can be configured via environment variables (see `.env.example`):

- `API_V1_PREFIX` - API route prefix (default: `/api/v1`)
- `PORT` - Server port (default: `5000`)
- `HOST` - Server host (default: `0.0.0.0`)
- `DEBUG` - Debug mode (default: `False`)
- `ALLOWED_ORIGINS` - CORS allowed origins

## Frontend Integration

The backend is configured to work with the frontend at:
- `http://localhost:8000` (default frontend port)

Update CORS settings in `.env` if using different ports.

## License

Academic Project | AI Coursework 2024

