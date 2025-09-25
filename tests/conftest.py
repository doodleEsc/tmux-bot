"""Pytest configuration and fixtures for tmux-bot tests."""

import pytest
from tmuxbot.config.settings import ProfileConfig, ModelSettings, Config, AgentConfig


@pytest.fixture
def valid_profile_config():
    """Create a valid ProfileConfig for testing."""
    return ProfileConfig(
        provider="openai",
        api_key="test-api-key-12345",
        model="gpt-3.5-turbo",
        base_url=None,
        settings=None
    )


@pytest.fixture
def profile_config_with_base_url():
    """Create a ProfileConfig with custom base URL."""
    return ProfileConfig(
        provider="openai",
        api_key="test-api-key-12345",
        model="gpt-4",
        base_url="https://api.openai.com/v1",
        settings=None
    )


@pytest.fixture
def profile_config_with_settings():
    """Create a ProfileConfig with model settings."""
    settings = ModelSettings(
        temperature=0.7,
        max_tokens=100
    )
    return ProfileConfig(
        provider="openai",
        api_key="test-api-key-12345",
        model="gpt-3.5-turbo",
        base_url=None,
        settings=settings
    )


@pytest.fixture
def profile_config_missing_api_key():
    """Create a ProfileConfig with missing API key."""
    return ProfileConfig(
        provider="openai",
        api_key="",
        model="gpt-3.5-turbo",
        base_url=None,
        settings=None
    )


@pytest.fixture
def profile_config_missing_model():
    """Create a ProfileConfig with missing model."""
    return ProfileConfig(
        provider="openai",
        api_key="test-api-key-12345",
        model="",
        base_url=None,
        settings=None
    )


@pytest.fixture
def profile_config_none_api_key():
    """Create a ProfileConfig with None API key."""
    return ProfileConfig(
        provider="openai",
        api_key=None,
        model="gpt-3.5-turbo",
        base_url=None,
        settings=None
    )


@pytest.fixture
def profile_config_none_model():
    """Create a ProfileConfig with None model."""
    return ProfileConfig(
        provider="openai",
        api_key="test-api-key-12345",
        model=None,
        base_url=None,
        settings=None
    )


@pytest.fixture
def mock_agent_config():
    """Create a valid AgentConfig for testing."""
    return AgentConfig(
        profile="openai-gpt-4",
        instructions="You are a test agent.",
        fallbacks=["openai-gpt-4o-mini"]
    )


@pytest.fixture
def invalid_agent_config():
    """Create an invalid AgentConfig for testing."""
    return AgentConfig(
        profile="nonexistent-profile",
        instructions="Invalid agent config.",
        fallbacks=None
    )


@pytest.fixture
def mock_config(valid_profile_config, mock_agent_config):
    """Create a mock Config for testing."""
    return Config(
        profiles={"openai-gpt-4": valid_profile_config},
        agents={"primary": mock_agent_config},
        max_history=100,
        conversation_timeout=300
    )


@pytest.fixture
def mock_config_missing_agent():
    """Create a Config without the requested agent."""
    return Config(
        profiles={"openai-gpt-4": ProfileConfig(
            provider="openai",
            api_key="test-key",
            model="gpt-4",
            base_url=None,
            settings=None
        )},
        agents={},  # No agents configured
        max_history=100,
        conversation_timeout=300
    )


@pytest.fixture
def mock_config_missing_profile(mock_agent_config):
    """Create a Config without the requested profile."""
    return Config(
        profiles={},  # No profiles configured
        agents={"primary": mock_agent_config},
        max_history=100,
        conversation_timeout=300
    )


@pytest.fixture
def mock_valid_profile(valid_profile_config):
    """Alias for valid_profile_config for factory tests."""
    return valid_profile_config