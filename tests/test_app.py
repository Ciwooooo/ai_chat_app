"""Tests for the FastAPI application."""

from fastapi.testclient import TestClient

from ai_chat.app import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_index_page():
    """Test index page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Chat" in response.text


def test_clear_chat():
    """Test clearing chat returns 200."""
    response = client.post("/clear")
    assert response.status_code == 200
