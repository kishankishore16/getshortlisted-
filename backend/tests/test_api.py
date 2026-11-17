"""API endpoint smoke tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "GetShortlisted API"


def test_root_index():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "GetShortlisted" in data["message"]
