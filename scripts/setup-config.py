#!/usr/bin/env python3
"""
TmuxBot Configuration Setup and Validation Script

This script helps set up, validate, and test TmuxBot configuration.

Usage:
    python scripts/setup-config.py --validate
    python scripts/setup-config.py --create-env
    python scripts/setup-config.py --test-providers
    python scripts/setup-config.py --full-check
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tmuxbot.config.settings import load_config, validate_config, save_config_template
    from tmuxbot.config.provider_config import ProviderConfigManager
    from tmuxbot.config.agent_config import AgentConfigManager
    from tmuxbot.providers.manager import ProviderManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)


class ConfigSetup:
    """Configuration setup and validation utility."""

    def __init__(self):
        self.project_root = project_root
        self.config_dir = self.project_root / "config"

    def validate_main_config(self) -> bool:
        """Validate the main configuration."""
        print("🔍 Validating main configuration...")

        try:
            config = load_config()
            is_valid = validate_config(config)

            if is_valid:
                print("✅ Main configuration is valid")
                print(f"   Primary model: {config.primary_model}")
                print(f"   Use OpenRouter: {config.use_openrouter}")
                print(f"   API timeout: {config.api_timeout}s")
                return True
            else:
                print("❌ Main configuration validation failed")
                return False

        except Exception as e:
            print(f"❌ Error validating main configuration: {e}")
            return False

    def validate_provider_configs(self) -> bool:
        """Validate provider configurations."""
        print("🔍 Validating provider configurations...")

        try:
            provider_config_manager = ProviderConfigManager()
            provider_configs = provider_config_manager.load_all_provider_configs()

            if not provider_configs:
                print("⚠️  No provider configurations found")
                return False

            print(f"✅ Loaded {len(provider_configs)} provider configurations:")

            all_valid = True
            for name, config in provider_configs.items():
                try:
                    validation_result = provider_config_manager.validate_config(config)

                    if validation_result['valid']:
                        print(f"   ✅ {name}: Valid")
                    else:
                        print(f"   ❌ {name}: Invalid - {validation_result['errors']}")
                        all_valid = False

                except Exception as e:
                    print(f"   ❌ {name}: Validation error - {e}")
                    all_valid = False

            return all_valid

        except Exception as e:
            print(f"❌ Error validating provider configurations: {e}")
            return False

    def validate_agent_configs(self) -> bool:
        """Validate agent configurations."""
        print("🔍 Validating agent configurations...")

        try:
            agent_config_manager = AgentConfigManager()

            # Test loading agent configurations
            from tmuxbot.config.agent_config import AgentType

            agent_types = [AgentType.PRIMARY, AgentType.CODER, AgentType.DEVOPS, AgentType.SYSADMIN]
            valid_count = 0

            for agent_type in agent_types:
                try:
                    providers = agent_config_manager.get_preferred_providers(agent_type)
                    print(f"   ✅ {agent_type.value}: {len(providers) if providers else 0} providers configured")
                    if providers:
                        valid_count += 1
                except Exception as e:
                    print(f"   ⚠️  {agent_type.value}: {e}")

            if valid_count > 0:
                print(f"✅ Agent configurations loaded ({valid_count}/{len(agent_types)} have provider configs)")
                return True
            else:
                print("⚠️  No agent-specific provider configurations found (using defaults)")
                return True  # This is not an error, just uses defaults

        except Exception as e:
            print(f"❌ Error validating agent configurations: {e}")
            return False

    async def test_providers(self) -> bool:
        """Test provider system integration."""
        print("🔍 Testing provider system...")

        try:
            # Load configurations
            config = load_config()
            provider_config_manager = ProviderConfigManager()
            provider_configs = provider_config_manager.load_all_provider_configs()

            if not provider_configs:
                print("❌ No provider configurations available for testing")
                return False

            # Create provider manager
            provider_manager = ProviderManager()

            # Register providers
            for name, provider_config in provider_configs.items():
                provider_manager.register_provider(name, provider_config)
                print(f"   ✅ Registered provider: {name}")

            # Test model creation
            test_models = ["gpt-4o", "gpt-4o-mini"]

            for model_name in test_models:
                try:
                    model_str = await provider_manager.create_model(model_name)
                    print(f"   ✅ Created model '{model_name}': {model_str}")
                except Exception as e:
                    print(f"   ⚠️  Failed to create model '{model_name}': {e}")

            # Test provider validation
            for provider_name, provider_status in provider_manager.providers.items():
                try:
                    validation_result = await provider_status.provider.validate_config()
                    status = "✅" if validation_result.get('valid', False) else "⚠️"
                    print(f"   {status} Provider {provider_name} validation: {validation_result.get('status', 'unknown')}")
                except Exception as e:
                    print(f"   ⚠️  Provider {provider_name} validation failed: {e}")

            print("✅ Provider system test completed")
            return True

        except Exception as e:
            print(f"❌ Error testing provider system: {e}")
            import traceback
            traceback.print_exc()
            return False

    def check_environment_variables(self) -> bool:
        """Check required environment variables."""
        print("🔍 Checking environment variables...")

        required_vars = {
            "OPENAI_API_KEY": "OpenAI API access",
            "OPENROUTER_API_KEY": "OpenRouter API access (optional)",
            "ANTHROPIC_API_KEY": "Anthropic API access (optional)"
        }

        found_vars = {}
        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            found_vars[var_name] = value is not None

            if value:
                # Show masked version for security
                if len(value) > 8:
                    masked = value[:6] + "..." + value[-4:]
                else:
                    masked = "***"
                print(f"   ✅ {var_name}: {masked}")
            else:
                print(f"   ⚠️  {var_name}: Not set ({description})")

        # Check if at least one provider key is available
        has_provider_key = found_vars["OPENAI_API_KEY"] or found_vars["OPENROUTER_API_KEY"]

        if has_provider_key:
            print("✅ At least one provider API key is configured")
            return True
        else:
            print("❌ No provider API keys found - set OPENAI_API_KEY or OPENROUTER_API_KEY")
            return False

    def check_config_files(self) -> bool:
        """Check configuration file structure."""
        print("🔍 Checking configuration files...")

        required_files = [
            "config.json",
            "config/providers/openai.yaml",
            "config/providers/openrouter.yaml",
            "config/agents/agents.yaml",
            "config/environments/development.yaml"
        ]

        optional_files = [
            "config/environments/production.yaml",
            "config/environments/staging.yaml",
            ".env",
            ".env.template"
        ]

        all_found = True

        print("   Required files:")
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} (missing)")
                all_found = False

        print("   Optional files:")
        for file_path in optional_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ⚠️  {file_path} (not found)")

        return all_found

    def create_env_template(self) -> bool:
        """Create .env file from template."""
        print("🔧 Creating .env file from template...")

        env_template = self.project_root / ".env.template"
        env_file = self.project_root / ".env"

        if not env_template.exists():
            print("❌ .env.template not found")
            return False

        if env_file.exists():
            response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("📋 Keeping existing .env file")
                return True

        try:
            # Copy template to .env
            with open(env_template, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())

            print("✅ Created .env file from template")
            print("📝 Please edit .env and add your API keys")
            return True

        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False

    def create_missing_configs(self) -> bool:
        """Create missing configuration files with defaults."""
        print("🔧 Creating missing configuration files...")

        try:
            # Create main config.json if missing
            config_json = self.project_root / "config.json"
            if not config_json.exists():
                save_config_template()
                print("   ✅ Created config.json template")

            # Additional configuration creation logic could go here
            # For now, the existing YAML files should be sufficient

            return True

        except Exception as e:
            print(f"❌ Error creating configuration files: {e}")
            return False


def main():
    """Main script entry point."""
    parser = argparse.ArgumentParser(description="TmuxBot Configuration Setup and Validation")
    parser.add_argument("--validate", action="store_true", help="Validate all configurations")
    parser.add_argument("--create-env", action="store_true", help="Create .env file from template")
    parser.add_argument("--test-providers", action="store_true", help="Test provider system")
    parser.add_argument("--full-check", action="store_true", help="Run full configuration check")
    parser.add_argument("--setup", action="store_true", help="Set up missing configuration files")

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    setup = ConfigSetup()

    print("🚀 TmuxBot Configuration Setup and Validation")
    print("=" * 50)

    success = True

    if args.create_env:
        success &= setup.create_env_template()

    if args.setup:
        success &= setup.create_missing_configs()

    if args.validate or args.full_check:
        success &= setup.check_config_files()
        success &= setup.check_environment_variables()
        success &= setup.validate_main_config()
        success &= setup.validate_provider_configs()
        success &= setup.validate_agent_configs()

    if args.test_providers or args.full_check:
        success &= asyncio.run(setup.test_providers())

    print("\n" + "=" * 50)

    if success:
        print("🎉 Configuration check completed successfully!")
        print("Your TmuxBot configuration is ready to use.")
    else:
        print("❌ Configuration check found issues.")
        print("Please review the errors above and fix them.")
        sys.exit(1)


if __name__ == "__main__":
    main()