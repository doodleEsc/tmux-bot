from pydantic_ai import ModelSettings
from tmuxbot.config.settings import ProfileConfig
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


def create_model(profile: ProfileConfig) -> Model:
    """Create OpenAI model from profile configuration.

    Args:
        profile: Configuration containing API key, model, and optional settings.
                 Must include valid api_key and model name.

    Returns:
        Configured OpenAI chat model ready for use.

    Raises:
        ValueError: If required fields (api_key, model) are missing or empty.
        ConnectionError: If unable to connect to OpenAI API or create provider.

    Example:
        >>> profile = ProfileConfig(
        ...     provider="openai",
        ...     api_key="sk-...",
        ...     model="gpt-3.5-turbo"
        ... )
        >>> model = create_model(profile)
    """
    # Input validation
    if not profile.api_key:
        raise ValueError("API key is required")
    if not profile.model:
        raise ValueError("Model name is required")

    base_url = profile.base_url
    api_key = profile.api_key
    model_name = profile.model
    settings = profile.settings

    # Basic settings validation (preserving backward compatibility)
    if settings is not None and not isinstance(settings, dict):
        raise ValueError("Settings must be a dictionary or None")

    try:
        provider = OpenAIProvider(base_url=base_url, api_key=api_key)
        return OpenAIChatModel(model_name, provider=provider, settings=settings)
    except Exception as e:
        raise ConnectionError(f"Failed to create OpenAI model: {e}") from e
