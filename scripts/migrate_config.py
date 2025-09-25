#!/usr/bin/env python3
"""
Configuration Migration Script: JSON to YAML

Converts existing config.json and profile JSON files to YAML format.
"""

import json
import sys
from pathlib import Path
from tmuxbot.config.yaml_utils import convert_json_comments_to_yaml, safe_dump_yaml


def migrate_main_config():
    """Migrate main config.json to config.yaml."""
    json_file = Path("config.json")
    yaml_file = Path("config.yaml")

    if not json_file.exists():
        print("No config.json found - nothing to migrate")
        return True

    if yaml_file.exists():
        response = input("config.yaml already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping main config migration")
            return True

    try:
        with open(json_file, 'r') as f:
            json_data = json.load(f)

        # Convert JSON comments to YAML comments
        yaml_content = convert_json_comments_to_yaml(json_data)

        with open(yaml_file, 'w') as f:
            f.write(yaml_content)

        print(f"Migrated {json_file} -> {yaml_file}")

        # Ask about backup
        response = input("Keep config.json as backup? (Y/n): ")
        if response.lower() not in ['n', 'no']:
            backup_file = json_file.with_suffix('.json.bak')
            json_file.rename(backup_file)
            print(f"Backed up to {backup_file}")
        else:
            json_file.unlink()
            print("Removed config.json")

        return True

    except Exception as e:
        print(f"Failed to migrate config.json: {e}")
        return False


def migrate_profile_directory():
    """Migrate profile JSON files to YAML."""
    profiles_dir = Path("profiles")
    if not profiles_dir.exists():
        print("No profiles directory found")
        return True

    json_files = list(profiles_dir.glob("*.json"))
    if not json_files:
        print("No profile JSON files found")
        return True

    success_count = 0
    for json_file in json_files:
        yaml_file = json_file.with_suffix('.yaml')

        if yaml_file.exists():
            print(f"Skipping {json_file.name} - YAML version exists")
            continue

        try:
            with open(json_file, 'r') as f:
                json_data = json.load(f)

            if safe_dump_yaml(json_data, yaml_file):
                print(f"Migrated {json_file.name} -> {yaml_file.name}")
                json_file.unlink()
                success_count += 1
            else:
                print(f"Failed to migrate {json_file.name}")

        except Exception as e:
            print(f"Failed to migrate {json_file.name}: {e}")

    print(f"Migrated {success_count}/{len(json_files)} profile files")
    return success_count == len(json_files)


def main():
    """Run the migration process."""
    print("TmuxBot Configuration Migration: JSON -> YAML")
    print("=" * 50)

    success = True

    # Migrate main configuration
    print("\n1. Migrating main configuration...")
    success &= migrate_main_config()

    # Migrate profile configurations
    print("\n2. Migrating profile configurations...")
    success &= migrate_profile_directory()

    print("\n" + "=" * 50)
    if success:
        print("Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test your configuration: python -c \"from tmuxbot.config.settings import load_config; print(load_config())\"")
        print("2. Run your tests to ensure compatibility")
    else:
        print("Migration completed with errors. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()