#!/usr/bin/env python3
"""
Update Claude Desktop configuration to add ChimeraX MCP server.
This script safely updates the config file, preserving existing entries.
"""

import json
import os
import sys
from pathlib import Path
import shutil


def get_claude_config_path():
    """Get the path to Claude Desktop config file."""
    appdata = os.getenv('APPDATA')
    if not appdata:
        raise RuntimeError("APPDATA environment variable not found")

    return Path(appdata) / "Claude" / "claude_desktop_config.json"


def backup_config(config_path):
    """Create a backup of the existing config file."""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)
        return backup_path
    return None


def load_config(config_path):
    """Load existing config or return empty structure."""
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Existing config is invalid JSON. Creating backup and starting fresh.")
            backup_config(config_path)
            return {}
    return {}


def update_config(config, exe_path):
    """
    Update config with ChimeraX MCP server entry.
    Preserves existing entries, prevents duplicates.
    """
    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add or update chimerax entry
    config["mcpServers"]["chimerax"] = {
        "command": str(exe_path)
    }

    return config


def save_config(config_path, config):
    """Save config file with proper formatting."""
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Write with nice formatting
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add trailing newline


def main(exe_path=None):
    """Main function to update Claude Desktop config."""
    if exe_path is None:
        if len(sys.argv) > 1:
            exe_path = sys.argv[1]
        else:
            # Default installation path
            exe_path = r"C:\Program Files\ChimeraX-MCP\chimerax-mcp-server.exe"

    exe_path = Path(exe_path)

    print(f"Updating Claude Desktop configuration...")
    print(f"Executable path: {exe_path}")

    try:
        # Get config path
        config_path = get_claude_config_path()
        print(f"Config file: {config_path}")

        # Backup existing config
        backup_path = backup_config(config_path)
        if backup_path:
            print(f"Backup created: {backup_path}")

        # Load existing config
        config = load_config(config_path)

        # Check if chimerax already exists
        if "mcpServers" in config and "chimerax" in config["mcpServers"]:
            existing_path = config["mcpServers"]["chimerax"].get("command", "")
            print(f"\nExisting ChimeraX MCP entry found: {existing_path}")
            print(f"Updating to: {exe_path}")
        else:
            print(f"\nAdding new ChimeraX MCP entry")

        # Update config
        config = update_config(config, exe_path)

        # Save config
        save_config(config_path, config)

        print(f"\n[SUCCESS] Configuration updated successfully!")
        print(f"\nNext steps:")
        print(f"  1. Restart Claude Desktop")
        print(f"  2. Start ChimeraX and run: remotecontrol rest start")
        print(f"  3. Ask Claude: 'What ChimeraX tools do you have?'")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Error updating configuration: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
