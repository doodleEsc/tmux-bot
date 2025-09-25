"""Mock provider module for testing ModelFactory."""

from pydantic_ai.models import Model
from unittest.mock import Mock

from tmuxbot.config.settings import ProfileConfig


def create_model(profile: ProfileConfig) -> Model:
    """Create a mock model for testing purposes.

    Args:
        profile: Configuration containing provider settings.

    Returns:
        A mock Model instance for testing.

    Raises:
        ValueError: If required fields are missing (for testing error scenarios).
    """
    # Basic validation (mirrors real provider validation)
    if not profile.api_key:
        raise ValueError("API key is required")
    if not profile.model:
        raise ValueError("Model name is required")

    # Return a mock model with some basic attributes
    mock_model = Mock(spec=Model)
    mock_model.provider_name = profile.provider
    mock_model.model_name = profile.model
    mock_model.api_key = profile.api_key
    mock_model.base_url = profile.base_url
    mock_model.settings = profile.settings

    return mock_model


def create_model_with_error(profile: ProfileConfig) -> Model:
    """Mock create_model function that always raises an error."""
    raise Exception("Mock provider error for testing")


# Mock module attributes for testing different scenarios
MOCK_PROVIDER_NAME = "mock_provider"
MOCK_MODEL_TYPES = ["mock-gpt-1", "mock-gpt-2", "mock-claude-1"]