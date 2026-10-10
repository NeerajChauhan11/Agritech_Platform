"""Pytest fixtures for API testing."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Provide a TestClient instance."""
    return TestClient(app)
