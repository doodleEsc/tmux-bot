"""Simplified tests for ModelFactory class to avoid mocking conflicts."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from tmuxbot.model.factory import ModelFactory


class TestModelFactorySimple:
    """Simplified test cases for ModelFactory class."""

    def test_agent_not_found(self, mock_config_missing_agent):
        """Test error handling when agent configuration is not found."""
        factory = ModelFactory(mock_config_missing_agent)

        with patch('tmuxbot.model.factory.logger') as mock_logger:
            result = factory.create_model("nonexistent-agent")

            # Verify None return and error logging
            assert result is None
            mock_logger.error.assert_called_once_with(
                "Agent configuration not found: nonexistent-agent"
            )

    def test_profile_not_found(self, mock_config_missing_profile):
        """Test error handling when profile is not found."""
        factory = ModelFactory(mock_config_missing_profile)
        result = factory.create_model("primary")

        # Verify None return when profile not found
        assert result is None

    def test_empty_agent_type(self, mock_config):
        """Test edge case with empty agent type."""
        factory = ModelFactory(mock_config)

        with patch('tmuxbot.model.factory.logger') as mock_logger:
            result = factory.create_model("")

            assert result is None
            mock_logger.error.assert_called_once_with(
                "Agent configuration not found: "
            )

    def test_factory_initialization(self, mock_config):
        """Test ModelFactory initialization."""
        factory = ModelFactory(mock_config)
        assert factory.config == mock_config

    def test_import_error_handling(self, mock_config):
        """Test ImportError is properly handled."""
        # Patch the import to raise ImportError
        with patch('tmuxbot.model.factory.importlib.import_module') as mock_import:
            mock_import.side_effect = ImportError("No module named 'tmuxbot.providers.nonexistent'")

            factory = ModelFactory(mock_config)

            with pytest.raises(ValueError, match="Unsupported provider specified"):
                factory.create_model("primary")

    def test_create_model_with_valid_provider(self, mock_config):
        """Test successful model creation with real provider import."""
        # Use the real openai provider import but mock the pydantic_ai components
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            # Setup mocks for pydantic_ai components
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider

            mock_model = Mock()
            mock_model_class.return_value = mock_model

            factory = ModelFactory(mock_config)
            result = factory.create_model("primary")

            # Verify that the real provider was called correctly
            assert result == mock_model
            mock_provider_class.assert_called_once()
            mock_model_class.assert_called_once()

    def test_logger_debug_message(self, mock_config):
        """Test that logger.debug is called with profile info."""
        with patch('tmuxbot.model.factory.logger') as mock_logger, \
             patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider

            mock_model = Mock()
            mock_model_class.return_value = mock_model

            factory = ModelFactory(mock_config)
            result = factory.create_model("primary")

            # Verify debug messages were logged
            expected_profile = mock_config.profiles["openai-gpt-4"]
            debug_calls = [call.args[0] for call in mock_logger.debug.call_args_list]

            # Check that both debug messages were called
            expected_profile_msg = f"Using profile: {expected_profile.provider}:{expected_profile.model}"
            expected_import_msg = "Successfully imported provider module: tmuxbot.providers.openai"

            assert expected_profile_msg in debug_calls
            assert expected_import_msg in debug_calls

    def test_attribute_error_handling(self, mock_config):
        """Test AttributeError is properly handled."""
        with patch('tmuxbot.model.factory.importlib.import_module') as mock_import:
            # Create a mock module that doesn't have create_model
            mock_provider_module = Mock()
            del mock_provider_module.create_model  # Remove create_model attribute
            mock_import.return_value = mock_provider_module

            factory = ModelFactory(mock_config)

            # The None return from getattr triggers ValueError which becomes RuntimeError
            with pytest.raises(RuntimeError, match="An unexpected error occurred while loading provider"):
                factory.create_model("primary")

    def test_create_model_function_none(self, mock_config):
        """Test when getattr returns None for create_model."""
        with patch('tmuxbot.model.factory.importlib.import_module') as mock_import:
            mock_provider_module = Mock()
            # Mock getattr to return None for create_model
            mock_provider_module.create_model = None
            mock_import.return_value = mock_provider_module

            factory = ModelFactory(mock_config)

            # The None value triggers ValueError which becomes RuntimeError in exception handling
            with pytest.raises(RuntimeError, match="An unexpected error occurred while loading provider"):
                factory.create_model("primary")

    def test_unexpected_exception_handling(self, mock_config):
        """Test unexpected exception handling."""
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class:
            # Make the provider constructor raise an unexpected exception
            mock_provider_class.side_effect = Exception("Unexpected error")

            factory = ModelFactory(mock_config)

            with pytest.raises(RuntimeError, match="An unexpected error occurred while loading provider"):
                factory.create_model("primary")