"""Tests for API endpoint."""

import pytest
from fastapi.testclient import TestClient
from src.api.server import app
from src.config import settings


client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()


def test_quiz_endpoint_invalid_json():
    """Test quiz endpoint with invalid JSON."""
    response = client.post(
        "/quiz",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400


def test_quiz_endpoint_invalid_secret():
    """Test quiz endpoint with invalid secret."""
    response = client.post(
        "/quiz",
        json={
            "email": settings.email,
            "secret": "wrong-secret",
            "url": "https://example.com/quiz"
        }
    )
    assert response.status_code == 403


def test_quiz_endpoint_invalid_email():
    """Test quiz endpoint with invalid email."""
    response = client.post(
        "/quiz",
        json={
            "email": "wrong@example.com",
            "secret": settings.secret,
            "url": "https://example.com/quiz"
        }
    )
    assert response.status_code == 403


def test_quiz_endpoint_valid_request():
    """Test quiz endpoint with valid request."""
    response = client.post(
        "/quiz",
        json={
            "email": settings.email,
            "secret": settings.secret,
            "url": "https://tds-llm-analysis.s-anand.net/demo"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_quiz_endpoint_missing_fields():
    """Test quiz endpoint with missing fields."""
    response = client.post(
        "/quiz",
        json={
            "email": settings.email,
            "secret": settings.secret
            # Missing 'url' field
        }
    )
    assert response.status_code == 400
