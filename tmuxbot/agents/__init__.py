"""Agent system for TmuxBot."""

import os
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional
# from .primary import create_primary_agent


@dataclass
class TmuxBotDeps:
    """
    Shared dependencies for TmuxBot agents.

    This dataclass provides dependency injection for all agents,
    containing session information, context, and system state.
    """

    tmux_session: Optional[Any] = None  # For future tmux integration
    conversation_history: List[Dict[str, str]] = field(
        default_factory=list
    )  # Conversation messages
    current_user: str = ""  # Current system user
    working_directory: str = ""  # Current working directory

    def __post_init__(self):
        """Initialize default values after creation."""

        if not self.current_user:
            self.current_user = os.getenv("USER", "unknown")

        if not self.working_directory:
            self.working_directory = os.getcwd()


def __getattr__(name: str) -> Any:
    """Lazy import to avoid circular import issues."""
    if name == "create_primary_agent":
        from .primary import create_primary_agent

        return create_primary_agent
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = ["TmuxBotDeps"]
