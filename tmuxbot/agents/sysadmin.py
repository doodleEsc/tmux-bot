"""System administration specialist agent for TmuxBot."""

import logging
from typing import Optional
from pydantic_ai import Agent

from ..config.settings import Config
from ..providers.manager import ProviderManager
from ..config.agent_config import AgentType, AgentConfigManager
from . import TmuxBotDeps

logger = logging.getLogger(__name__)


async def create_sysadmin_agent(config: Config, provider_manager: Optional[ProviderManager] = None) -> Agent[TmuxBotDeps, str]:
    """
    Create the system administration specialist agent with profile system integration.

    Args:
        config: TmuxBot configuration settings
        provider_manager: Optional provider manager for multi-provider support

    Returns:
        Agent[TmuxBotDeps, str]: Configured system admin agent
    """
    # Initialize agent configuration manager
    agent_config_mgr = AgentConfigManager()
    agent_mappings = agent_config_mgr.load_agent_mappings()

    # Get agent instructions from configuration if available
    agent_instructions = agent_config_mgr.get_agent_instructions(AgentType.SYSADMIN)

    # Create model using profile system or legacy approach
    model = None
    model_creation_method = "unknown"

    try:
        # Check if sysadmin agent uses profile-based configuration
        if agent_config_mgr.is_profile_based(AgentType.SYSADMIN):
            profile_name = agent_config_mgr.get_agent_profile(AgentType.SYSADMIN)

            if profile_name:
                logger.info(f"Creating sysadmin agent with profile: {profile_name}")
                from ..config.settings import ProfileFactory
                profile_factory = ProfileFactory(config)
                model = profile_factory.create_model_from_profile(profile_name)
                model_creation_method = f"profile:{profile_name}"

                # Get model parameters from profile for potential future use
                model_params = profile_factory.get_model_parameters(profile_name)
                logger.debug(f"Sysadmin agent model parameters: {model_params}")
            else:
                logger.warning("Sysadmin agent configured for profile-based but no profile specified")

        # If profile creation failed or not configured, try provider system
        if model is None and provider_manager is not None:
            logger.info("Trying provider system for sysadmin agent model creation")
            preferred_providers = agent_config_mgr.get_preferred_providers(AgentType.SYSADMIN)

            if preferred_providers:
                model = await provider_manager.create_model(
                    "gpt-4o",  # Default model for sysadmin
                    preferred_providers=preferred_providers
                )
                model_creation_method = "provider_system:gpt-4o"
            else:
                logger.warning("No preferred providers configured for sysadmin agent")

    except Exception as e:
        logger.warning(f"Failed to create model using profile/provider system for sysadmin: {e}")

    if model is None:
        try:
            logger.info("Attempting ProfileFactory fallback for sysadmin agent")
            from ..config.settings import ProfileFactory
            profile_factory = ProfileFactory(config)
            model = profile_factory.create_model("gpt-4o")  # Default sysadmin model
            model_creation_method = "profile_factory_fallback:gpt-4o"
        except Exception as e:
            logger.error(f"ProfileFactory fallback failed for sysadmin: {e}")
            raise RuntimeError("No profiles configured and could not create sysadmin agent model. Please configure at least one profile.")

    logger.info(f"Sysadmin agent created using: {model_creation_method}")

    # Use agent-specific instructions if configured, otherwise use default
    default_instructions = (
        "You are TmuxBot's system administration specialist. "
        "You help with server management, monitoring, troubleshooting, and system configuration. "
        "Provide safe and practical system administration guidance, "
        "prioritizing security, stability, and best practices."
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