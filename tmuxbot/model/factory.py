# Standard library imports
import importlib
import logging
from typing import Callable, Optional, cast

# Third-party imports
from pydantic_ai.models import Model

# Local imports
from ..config import Config

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory class for creating AI models based on configuration profiles.

    The ModelFactory dynamically loads AI provider modules and creates models
    according to agent configurations and provider profiles. It supports
    multiple AI providers through a plugin-like architecture.

    Attributes:
        config: TmuxBot configuration containing profiles and agent settings.

    Example:
        >>> config = load_config()
        >>> factory = ModelFactory(config)
        >>> model = factory.create_model("primary")
    """

    def __init__(self, config: Config) -> None:
        self.config = config

    def create_model(
        self,
        agent_type: str,
    ) -> Optional[Model]:
        """Create a model instance for the specified agent type.

        Dynamically loads the appropriate AI provider module based on the agent's
        profile configuration and creates a model instance using the provider's
        create_model function.

        Args:
            agent_type: The type of agent to create a model for (e.g., "primary", "coder").
                       Must match an agent configuration in the config.

        Returns:
            A configured AI model ready for use, or None if the agent configuration
            or profile is not found.

        Raises:
            ValueError: If the provider module doesn't exist or lacks a create_model function.
            RuntimeError: If an unexpected error occurs during model creation.

        Example:
            >>> factory = ModelFactory(config)
            >>> model = factory.create_model("primary")
            >>> if model:
            ...     response = model.generate("Hello, world!")
        """
        agent_config = self.config.agents.get(agent_type)
        if agent_config is None:
            logger.error(f"Agent configuration not found: {agent_type}")
            return None

        profile_name = agent_config.profile

        profile = self.config.profiles.get(profile_name, None)
        if profile is None:
            return None

        logger.debug(f"Using profile: {profile.provider}:{profile.model}")

        provider_name = profile.provider

        try:
            provider_module = importlib.import_module(
                f"tmuxbot.providers.{provider_name}"
            )

            logger.debug(
                f"Successfully imported provider module: tmuxbot.providers.{provider_name}"
            )

            create_model_attr = getattr(provider_module, "create_model", None)
            if create_model_attr is None:
                error_msg = f"Provider module '{provider_name}' does not have a 'create_model' function"
                raise ValueError(error_msg)

            create_model_func = cast(Callable[..., Model], create_model_attr)
            return create_model_func(profile)

        except ImportError as err:
            error_msg = f"Unsupported provider specified: '{provider_name}'. Could not find provider module 'tmuxbot.providers.{provider_name}'"
            logger.error(error_msg)
            raise ValueError(error_msg) from err

        except AttributeError as err:
            error_msg = f"Provider module '{provider_name}' does not have a 'create_model' function"
            logger.error(error_msg)
            raise ValueError(error_msg) from err

        except Exception as e:
            error_msg = f"An unexpected error occurred while loading provider '{provider_name}': {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
