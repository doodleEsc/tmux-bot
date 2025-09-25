"""YAML utility functions for TmuxBot conf        # Fallback to JSON template
        try:
            config_data["_comment"] = {
                "description": "TmuxBot Profile-Based Configuration",
                "architecture": "Pure profile-based - no legacy settings",
            }

            with open(json_config_file, "w") as f:
                json.dump(config_data, f, indent=2)
            logger.info("Created config.json template (YAML fallback)")

        except IOError:
            # Silently fail if we can't write any file
            pass
iguration."""

import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def safe_load_yaml(file_path: Path) -> Optional[Dict[str, Any]]:
    """Safely load YAML file with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (yaml.YAMLError, IOError) as e:
        logger.error(f"Failed to load YAML file {file_path}: {e}")
        return None


def safe_dump_yaml(data: Dict[str, Any], file_path: Path) -> bool:
    """Safely dump data to YAML file with error handling."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, indent=2, sort_keys=False)
        return True
    except (yaml.YAMLError, IOError) as e:
        logger.error(f"Failed to write YAML file {file_path}: {e}")
        return False


def convert_json_comments_to_yaml(data: Dict[str, Any]) -> str:
    """Convert JSON _comment fields to YAML comments."""
    yaml_lines = []

    def add_comments(obj: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Extract _comment fields and return cleaned data."""
        cleaned = {}
        comments = obj.get("_comment") or obj.get("_comments")

        if comments:
            if isinstance(comments, dict):
                for key, value in comments.items():
                    yaml_lines.append(f"{prefix}# {key}: {value}")
            elif isinstance(comments, str):
                yaml_lines.append(f"{prefix}# {comments}")

        for key, value in obj.items():
            if key not in ("_comment", "_comments"):
                if isinstance(value, dict):
                    # Recursively process nested dictionaries
                    cleaned[key] = add_comments(value, prefix)
                else:
                    cleaned[key] = value

        return cleaned

    # Process the data to extract comments
    if isinstance(data, dict):
        cleaned_data = add_comments(data)
    else:
        cleaned_data = data

    # Generate YAML content
    yaml_content = yaml.safe_dump(
        cleaned_data, default_flow_style=False, indent=2, sort_keys=False
    )

    # Combine comments and YAML content
    if yaml_lines:
        return "\n".join(yaml_lines) + "\n\n" + yaml_content
    return yaml_content
