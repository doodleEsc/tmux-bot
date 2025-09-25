"""Tests for OpenAI provider module."""

import pytest
from unittest.mock import Mock, patch
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from tmuxbot.providers.openai import create_model
from tmuxbot.config.settings import ProfileConfig


class TestCreateModel:
    """Test cases for create_model function."""

    def test_create_model_success(self, valid_profile_config):
        """Test successful model creation with valid configuration."""
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            # Setup mocks
            mock_provider = Mock(spec=OpenAIProvider)
            mock_provider_class.return_value = mock_provider

            mock_model = Mock(spec=OpenAIChatModel)
            mock_model_class.return_value = mock_model

            # Call function
            result = create_model(valid_profile_config)

            # Verify provider creation
            mock_provider_class.assert_called_once_with(
                base_url=None,
                api_key="test-api-key-12345"
            )

            # Verify model creation
            mock_model_class.assert_called_once_with(
                "gpt-3.5-turbo",
                provider=mock_provider,
                settings=None
            )

            # Verify return value
            assert result == mock_model

    def test_create_model_with_base_url(self, profile_config_with_base_url):
        """Test model creation with custom base URL."""
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            mock_provider = Mock(spec=OpenAIProvider)
            mock_provider_class.return_value = mock_provider

            mock_model = Mock(spec=OpenAIChatModel)
            mock_model_class.return_value = mock_model

            result = create_model(profile_config_with_base_url)

            # Verify base_url is passed correctly
            mock_provider_class.assert_called_once_with(
                base_url="https://api.openai.com/v1",
                api_key="test-api-key-12345"
            )

            assert result == mock_model

    def test_create_model_with_settings(self, profile_config_with_settings):
        """Test model creation with model settings."""
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            mock_provider = Mock(spec=OpenAIProvider)
            mock_provider_class.return_value = mock_provider

            mock_model = Mock(spec=OpenAIChatModel)
            mock_model_class.return_value = mock_model

            result = create_model(profile_config_with_settings)

            # Verify settings are passed correctly
            mock_model_class.assert_called_once_with(
                "gpt-3.5-turbo",
                provider=mock_provider,
                settings=profile_config_with_settings.settings
            )

            assert result == mock_model

    def test_create_model_missing_api_key(self, profile_config_missing_api_key):
        """Test error handling for missing API key."""
        with pytest.raises(ValueError, match="API key is required"):
            create_model(profile_config_missing_api_key)

    def test_create_model_missing_model(self, profile_config_missing_model):
        """Test error handling for missing model name."""
        with pytest.raises(ValueError, match="Model name is required"):
            create_model(profile_config_missing_model)

    def test_create_model_none_api_key(self, profile_config_none_api_key):
        """Test error handling for None API key."""
        with pytest.raises(ValueError, match="API key is required"):
            create_model(profile_config_none_api_key)

    def test_create_model_none_model(self, profile_config_none_model):
        """Test error handling for None model name."""
        with pytest.raises(ValueError, match="Model name is required"):
            create_model(profile_config_none_model)

    def test_create_model_connection_error(self, valid_profile_config):
        """Test error handling for connection failures."""
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class:
            # Simulate provider creation failure
            mock_provider_class.side_effect = Exception("API connection failed")

            with pytest.raises(ConnectionError, match="Failed to create OpenAI model: API connection failed"):
                create_model(valid_profile_config)

    def test_create_model_invalid_provider(self, valid_profile_config):
        """Test error handling for invalid provider creation."""
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            # Provider creation succeeds but model creation fails
            mock_provider = Mock(spec=OpenAIProvider)
            mock_provider_class.return_value = mock_provider
            mock_model_class.side_effect = Exception("Invalid model configuration")

            with pytest.raises(ConnectionError, match="Failed to create OpenAI model: Invalid model configuration"):
                create_model(valid_profile_config)

    def test_create_model_invalid_settings(self, valid_profile_config):
        """Test error handling for invalid settings type."""
        # Modify the profile to have invalid settings
        invalid_config = ProfileConfig(
            provider=valid_profile_config.provider,
            api_key=valid_profile_config.api_key,
            model=valid_profile_config.model,
            base_url=valid_profile_config.base_url,
            settings="invalid_settings"  # String instead of dict/None
        )

        with pytest.raises(ValueError, match="Settings must be a dictionary or None"):
            create_model(invalid_config)


class TestIntegration:
    """Integration tests for create_model function."""

    @patch('tmuxbot.providers.openai.OpenAIProvider')
    @patch('tmuxbot.providers.openai.OpenAIChatModel')
    def test_end_to_end_model_creation_flow(self, mock_model_class, mock_provider_class, valid_profile_config):
        """Test complete model creation workflow."""
        # Setup realistic mocks
        mock_provider = Mock(spec=OpenAIProvider)
        mock_provider_class.return_value = mock_provider

        mock_model = Mock(spec=OpenAIChatModel)
        mock_model_class.return_value = mock_model

        # Execute workflow
        result = create_model(valid_profile_config)

        # Verify complete workflow
        assert mock_provider_class.call_count == 1
        assert mock_model_class.call_count == 1
        assert result == mock_model

        # Verify call arguments match profile
        provider_call = mock_provider_class.call_args
        assert provider_call[1]['api_key'] == valid_profile_config.api_key
        assert provider_call[1]['base_url'] == valid_profile_config.base_url

        model_call = mock_model_class.call_args
        assert model_call[0][0] == valid_profile_config.model
        assert model_call[1]['provider'] == mock_provider
        assert model_call[1]['settings'] == valid_profile_config.settings

    def test_settings_parameter_propagation(self, profile_config_with_settings):
        """Test that model settings are properly propagated."""
        with patch('tmuxbot.providers.openai.OpenAIProvider') as mock_provider_class, \
             patch('tmuxbot.providers.openai.OpenAIChatModel') as mock_model_class:

            mock_provider = Mock(spec=OpenAIProvider)
            mock_provider_class.return_value = mock_provider

            mock_model = Mock(spec=OpenAIChatModel)
            mock_model_class.return_value = mock_model

            create_model(profile_config_with_settings)

            # Verify settings are passed through correctly
            model_call = mock_model_class.call_args
            passed_settings = model_call[1]['settings']
            original_settings = profile_config_with_settings.settings

            assert passed_settings == original_settings
            assert passed_settings['temperature'] == 0.7
            assert passed_settings['max_tokens'] == 100