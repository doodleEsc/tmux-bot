"""Configuration management for TmuxBot."""

import json
import os
import logging
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Union, Any, List
from pydantic_ai import ModelSettings

from ..utils.yaml_utils import safe_load_yaml

logger = logging.getLogger(__name__)


@dataclass
class ProfileConfig:
    provider: str
    api_key: str
    model: str
    base_url: Optional[str] = None
    settings: Optional[ModelSettings] = None


@dataclass
class AgentConfig:
    profile: str
    instructions: Optional[str] = None
    fallbacks: Optional[List[str]] = None


@dataclass
class Config:
    """TmuxBot configuration settings with profile-based architecture and conversation management."""

    profiles: Dict[str, ProfileConfig]
    agents: Dict[str, AgentConfig]
    max_history: int
    conversation_timeout: int


def load_config() -> Union[None, Config]:
    """
    Load configuration from YAML/JSON file and environment variables.

    Supports both config.yaml (preferred) and config.json (legacy) formats.
    Environment variables take precedence over file values.
    Uses TMUXBOT_ prefix for environment variables.

    Returns:
        Config: Loaded configuration with defaults for missing values
    """
    config_data = {}

    # Try loading YAML configuration first (preferred)
    yaml_config_file = Path(os.getcwd()) / "config.yaml"
    if yaml_config_file.exists():
        try:
            yaml_data = safe_load_yaml(yaml_config_file)
            if yaml_data:
                config_data = yaml_data
                logger.info("Loaded configuration from config.yaml")
        except Exception as e:
            logger.warning(f"Failed to load config.yaml: {e}")

    # Conversation management environment variables
    env_max_history = os.getenv("TMUXBOT_MAX_HISTORY")
    if env_max_history:
        try:
            history_value = int(env_max_history)
            if history_value > 0:
                config_data["max_history"] = history_value
        except ValueError:
            logger.warning(f"Invalid TMUXBOT_MAX_HISTORY value: {env_max_history}")

    env_conversation_timeout = os.getenv("TMUXBOT_CONVERSATION_TIMEOUT")
    if env_conversation_timeout:
        try:
            timeout_value = int(env_conversation_timeout)
            if timeout_value > 0:
                config_data["conversation_timeout"] = timeout_value
        except ValueError:
            logger.warning(
                f"Invalid TMUXBOT_CONVERSATION_TIMEOUT value: {env_conversation_timeout}"
            )

    # Profile-specific environment variables are handled by ProfileConfigManager

    # Create Config object with loaded data, using defaults for missing fields
    try:
        # Convert profile data to ProfileConfig objects
        profiles = {}
        profile_data = config_data.get("profiles", {})
        for profile_name, profile_info in profile_data.items():
            profiles[profile_name] = ProfileConfig(
                provider=profile_info["provider"],
                api_key=profile_info["api_key"],
                model=profile_info["model"],
                base_url=profile_info.get("base_url"),
                settings=profile_info.get("settings"),
            )

        # Convert agent data to AgentConfig objects
        agents = {}
        agent_data = config_data.get("agents", {})
        for agent_name, agent_info in agent_data.items():
            agents[agent_name] = AgentConfig(
                profile=agent_info["profile"],
                instructions=agent_info.get("instructions"),
                fallbacks=agent_info.get("fallbacks"),
            )

        config = Config(
            profiles=profiles,
            agents=agents,
            max_history=config_data.get("max_history", 100),
            conversation_timeout=config_data.get("conversation_timeout", 300),
        )

        return config
    except (TypeError, ValueError) as e:
        # Return default config if there are any issues
        logger.warning(f"Failed to load config: {e}")
        return None


def save_config_template() -> None:
    """
    Save a profile-based configuration template to config.yaml.
    Falls back to config.json if YAML writing fails.
    Only creates the file if neither config.yaml nor config.json exist.
    """
    yaml_config_file = Path(os.getcwd()) / "config.yaml"

    # Create profile-based configuration template
    config_data = {
        "profiles": {
            "openai-gpt-4o": {
                "provider": "openai",
                "model": "gpt-4o",
                "api_key": "your-openai-api-key-here",
                "base_url": None,
                "settings": None,
            },
            "openai-gpt-4o-mini": {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "api_key": "your-openai-api-key-here",
                "base_url": None,
                "settings": None,
            },
        },
        "agents": {
            "primary": {
                "profile": "openai-gpt-4o",
                "instructions": "You are TmuxBot's primary coordination agent.",
                "fallbacks": None,
            },
            "coder": {
                "profile": "openai-gpt-4o",
                "instructions": "Focus on code quality and best practices.",
                "fallbacks": ["openai-gpt-4o-mini"],
            },
        },
        "max_history": 100,
        "conversation_timeout": 300,
    }

    # Try to save as YAML first
    try:
        yaml_content = f"""# TmuxBot Profile-Based Configuration
# Pure profile-based architecture - no legacy settings
# Environment variables: Use TMUXBOT_PROFILE_{{PROFILE_NAME}}_{{PARAMETER}} to override settings

{yaml.safe_dump(config_data, default_flow_style=False, indent=2, sort_keys=False)}"""

        with open(yaml_config_file, "w") as f:
            f.write(yaml_content)
        logger.info("Created config.yaml template")

    except Exception as e:
        logger.warning(f"Failed to create YAML template: {e}")
