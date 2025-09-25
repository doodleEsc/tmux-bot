"""DevOps specialist agent for TmuxBot."""

import logging
from typing import Optional
from pydantic_ai import Agent

from ..config.settings import Config
from ..providers.manager import ProviderManager
from ..config.agent_config import AgentType, AgentConfigManager
from . import TmuxBotDeps

logger = logging.getLogger(__name__)


async def create_devops_agent(config: Config, provider_manager: Optional[ProviderManager] = None) -> Agent[TmuxBotDeps, str]:
    """
    Create the DevOps specialist agent with profile system integration.

    Args:
        config: TmuxBot configuration settings
        provider_manager: Optional provider manager for multi-provider support

    Returns:
        Agent[TmuxBotDeps, str]: Configured DevOps agent
    """
    # Initialize agent configuration manager
    agent_config_mgr = AgentConfigManager()
    agent_mappings = agent_config_mgr.load_agent_mappings()

    # Get agent instructions from configuration if available
    agent_instructions = agent_config_mgr.get_agent_instructions(AgentType.DEVOPS)

    # Create model using profile system or legacy approach
    model = None
    model_creation_method = "unknown"

    try:
        # Check if devops agent uses profile-based configuration
        if agent_config_mgr.is_profile_based(AgentType.DEVOPS):
            profile_name = agent_config_mgr.get_agent_profile(AgentType.DEVOPS)

            if profile_name:
                logger.info(f"Creating devops agent with profile: {profile_name}")
                from ..config.settings import ProfileFactory
                profile_factory = ProfileFactory(config)
                model = profile_factory.create_model_from_profile(profile_name)
                model_creation_method = f"profile:{profile_name}"

                # Get model parameters from profile for potential future use
                model_params = profile_factory.get_model_parameters(profile_name)
                logger.debug(f"DevOps agent model parameters: {model_params}")
            else:
                logger.warning("DevOps agent configured for profile-based but no profile specified")

        # If profile creation failed or not configured, try provider system
        if model is None and provider_manager is not None:
            logger.info("Trying provider system for devops agent model creation")
            preferred_providers = agent_config_mgr.get_preferred_providers(AgentType.DEVOPS)

            if preferred_providers:
                model = await provider_manager.create_model(
                    "gpt-4o",  # Default model for devops
                    preferred_providers=preferred_providers
                )
                model_creation_method = "provider_system:gpt-4o"
            else:
                logger.warning("No preferred providers configured for devops agent")

    except Exception as e:
        logger.warning(f"Failed to create model using profile/provider system for devops: {e}")

    if model is None:
        try:
            logger.info("Attempting ProfileFactory fallback for devops agent")
            from ..config.settings import ProfileFactory
            profile_factory = ProfileFactory(config)
            model = profile_factory.create_model("gpt-4o")  # Default devops model
            model_creation_method = "profile_factory_fallback:gpt-4o"
        except Exception as e:
            logger.error(f"ProfileFactory fallback failed for devops: {e}")
            raise RuntimeError("No profiles configured and could not create devops agent model. Please configure at least one profile.")

    logger.info(f"DevOps agent created using: {model_creation_method}")

    # Use agent-specific instructions if configured, otherwise use default
    default_instructions = (
        "You are TmuxBot's DevOps specialist. "
        "You help with deployment, CI/CD, infrastructure, and automation. "
        "Provide practical solutions for development operations, "
        "focusing on scalability, reliability, and security."
    )

    final_instructions = agent_instructions or default_instructions

    # Create agent with determined model
    agent = Agent(
        model=model,
        deps_type=TmuxBotDeps,
        output_type=str,
        instructions=final_instructions,
    )

    return agent