"""
Tests for prediction endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_health_endpoint():
    """Test API health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "model_loaded" in response.json()


def test_valid_prediction():
    """Test prediction with valid input"""
    response = client.post(
        "/api/v1/predict",
        json={
            "route_id": 3,
            "weather": "cloudy",
            "passenger_count": 120,
            "time_of_day": 1,
            "is_weekend": 0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_delay" in data
    assert "model_name" in data
    assert isinstance(data["predicted_delay"], (int, float))
    assert data["predicted_delay"] >= 0


def test_invalid_route_id():
    """Test prediction with invalid route_id"""
    response = client.post(
        "/api/v1/predict",
        json={
            "route_id": 15,  # Invalid: > 10
            "weather": "cloudy",
            "passenger_count": 120,
            "time_of_day": 1,
            "is_weekend": 0
        }
    )
    assert response.status_code == 422  # Validation error


def test_invalid_weather():
    """Test prediction with invalid weather"""
    response = client.post(
        "/api/v1/predict",
        json={
            "route_id": 3,
            "weather": "foggy",  # Invalid
            "passenger_count": 120,
            "time_of_day": 1,
            "is_weekend": 0
        }
    )
    assert response.status_code == 422  # Validation error


def test_invalid_passenger_count():
    """Test prediction with invalid passenger_count"""
    response = client.post(
        "/api/v1/predict",
        json={
            "route_id": 3,
            "weather": "cloudy",
            "passenger_count": 600,  # Invalid: > 500
            "time_of_day": 1,
            "is_weekend": 0
        }
    )
    assert response.status_code == 422  # Validation error


def test_feature_importance_endpoint():
    """Test feature importance endpoint"""
    response = client.get("/api/v1/feature-importance")
    assert response.status_code == 200
    data = response.json()
    assert "importances" in data
    assert "explanation" in data
    assert isinstance(data["importances"], list)


def test_weather_normalization():
    """Test that 'sunny' is normalized to 'clear'"""
    response = client.post(
        "/api/v1/predict",
        json={
            "route_id": 3,
            "weather": "sunny",  # Should be normalized to 'clear'
            "passenger_count": 120,
            "time_of_day": 1,
            "is_weekend": 0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "predicted_delay" in data

