# tmux-bot

## Configuration

TmuxBot supports both YAML (recommended) and JSON configuration formats:

- `config.yaml` - Primary configuration file (YAML format)
- `config.json` - Legacy configuration file (JSON format)

If both files exist, `config.yaml` takes precedence.

### Migration from JSON to YAML

To migrate existing JSON configuration to YAML format:

```bash
python scripts/migrate_config.py
```

This will convert `config.json` to `config.yaml` and handle profile files in the `profiles/` directory.