"""Main application entry point for TmuxBot."""

import sys
from rich.console import Console
from rich.panel import Panel

from .config import load_config
from .core import ConversationContext
from .agents import TmuxBotDeps, create_primary_agent


def run_tmuxbot() -> None:
    """
    Main application entry point for TmuxBot.

    Handles configuration loading, agent creation, and CLI launch
    with proper error handling and user feedback.
    """
    console = Console()

    try:
        # Display startup message
        console.print(
            Panel(
                "[bold blue]🤖 TmuxBot Phase 1[/bold blue]\n"
                "Terminal-based AI assistant starting up...",
                title="TmuxBot",
                border_style="blue",
            )
        )

        # Load and validate configuration
        console.print("Loading configuration...")
        config = load_config()

        # TODO: check if config is None, then exit

        # Create conversation context
        context = ConversationContext(max_messages=config.max_history)

        # Create agent dependencies
        deps = TmuxBotDeps(conversation_history=context.get_history())

        # Create primary agent
        console.print("Initializing AI agent...")
        try:
            agent = create_primary_agent(config)
        except Exception as e:
            console.print(
                Panel(
                    f"[red]Failed to initialize AI agent![/red]\n\n"
                    f"Error: {str(e)}\n\n"
                    "Please check:\n"
                    "• Your API keys are set correctly\n"
                    "• Network connection is working\n"
                    "• Model names are valid\n\n"
                    "For OpenAI: Set OPENAI_API_KEY environment variable\n"
                    "For Anthropic: Set ANTHROPIC_API_KEY environment variable",
                    title="Agent Initialization Error",
                    border_style="red",
                )
            )
            sys.exit(1)

        # Display ready message
        console.print(
            Panel(
                "[green]✅ TmuxBot is ready![/green]\n\n"
                "You can now chat with your AI assistant.\n"
                "Type your questions and I'll help you with coding, research, and more.\n\n"
                "[dim]Available commands:[/dim]\n"
                "• /exit - Close session (Ctrl-C, Ctrl-D also work)\n"
                "• /markdown - Show last response in markdown\n"
                "• /multiline - Toggle multiline input mode\n"
                "• /cp - Copy last response to clipboard\n\n"
                "[bold]Ready for your questions![/bold]",
                title="Ready",
                border_style="green",
            )
        )

        # Launch interactive CLI
        # Note: We use to_cli_sync() for synchronous operation in Phase 1
        agent.to_cli_sync(deps=deps)

    except KeyboardInterrupt:
        console.print("\n[yellow]👋 TmuxBot shutting down... Goodbye![/yellow]")

    except ImportError as e:
        console.print(
            Panel(
                f"[red]Missing required dependencies![/red]\n\n"
                f"Error: {str(e)}\n\n"
                "Please install required packages:\n"
                "pip install pydantic-ai-slim[cli,mcp,openai]",
                title="Dependency Error",
                border_style="red",
            )
        )
        sys.exit(1)

    except Exception as e:
        console.print(
            Panel(
                f"[red]Unexpected error occurred![/red]\n\n"
                f"Error: {str(e)}\n\n"
                "Please check:\n"
                "• Your configuration is correct\n"
                "• API keys are valid\n"
                "• Network connection is working\n\n"
                "If the problem persists, please report it as a bug.",
                title="Unexpected Error",
                border_style="red",
            )
        )
        sys.exit(1)
