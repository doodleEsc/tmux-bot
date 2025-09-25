"""In-memory conversation context management for TmuxBot."""

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ConversationContext:
    """
    Manages conversation history and context for TmuxBot sessions.

    For Phase 1, this provides simple in-memory context management
    with automatic truncation to prevent memory bloat.
    """

    messages: List[Dict[str, str]] = field(default_factory=list)
    max_messages: int = 50

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation context.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        self.messages.append({"role": role, "content": content})

        # Automatic context truncation to prevent memory issues
        if len(self.messages) > self.max_messages:
            # Keep first message (usually system prompt) and recent messages
            if len(self.messages) > 1:
                self.messages = [self.messages[0]] + self.messages[
                    -(self.max_messages - 1) :
                ]
            else:
                self.messages = self.messages[-self.max_messages :]

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the full conversation history.

        Returns:
            List[Dict[str, str]]: List of message dictionaries
        """
        return self.messages.copy()

    def get_recent_messages(self, count: int = 10) -> List[Dict[str, str]]:
        """
        Get the most recent messages.

        Args:
            count: Number of recent messages to return

        Returns:
            List[Dict[str, str]]: List of recent message dictionaries
        """
        return (
            self.messages[-count:]
            if len(self.messages) > count
            else self.messages.copy()
        )

    def clear_context(self) -> None:
        """Clear all messages from the conversation context."""
        self.messages.clear()

    def get_message_count(self) -> int:
        """
        Get the total number of messages in context.

        Returns:
            int: Number of messages
        """
        return len(self.messages)

    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current context state.

        Returns:
            Dict[str, Any]: Context summary with message count and truncation info
        """
        return {
            "message_count": len(self.messages),
            "max_messages": self.max_messages,
            "is_at_limit": len(self.messages) >= self.max_messages,
            "has_messages": len(self.messages) > 0,
        }
