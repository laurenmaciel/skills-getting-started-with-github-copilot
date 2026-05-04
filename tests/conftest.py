"""Pytest configuration and shared fixtures."""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Provide a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Provide a sample email for testing."""
    return "test.student@mergington.edu"


@pytest.fixture
def existing_activity():
    """Provide an existing activity name for testing."""
    return "Chess Club"


@pytest.fixture
def non_existent_activity():
    """Provide a non-existent activity name for testing."""
    return "Nonexistent Activity"


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities to original state before each test.
    This ensures test isolation and prevents state leakage between tests.
    """
    # Store original state
    original_activities = copy.deepcopy(activities)

    yield

    # Restore original state after test
    activities.clear()
    activities.update(original_activities)