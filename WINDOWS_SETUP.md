# ChimeraX MCP Server - Windows Setup Guide

## Working Configuration (October 2025)

This document describes the **working setup** for running the ChimeraX MCP Server on Windows with Claude Desktop.

## Prerequisites

- **UCSF ChimeraX** installed and accessible
- **Python 3.8+** (tested with Python 3.14)
- **Claude Desktop** installed
- **Git** for version control

## Installation Steps

### 1. Clone the Repository

```bash
cd C:\projects\mcp
gh repo clone jessicalh/chimerax-mcp
cd chimerax-mcp
```

### 2. Install Python Dependencies

```bash
pip install mcp requests
```

### 3. Configure ChimeraX Port (Optional)

The server expects ChimeraX REST API on port 50960 by default. Check `chimerax_mcp_config.json`:

```json
{
  "port": 50960
}
```

### 4. Configure Claude Desktop

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "chimerax": {
      "command": "python",
      "args": [
        "C:\\projects\\mcp\\chimerax-mcp\\chimerax_mcp_server.py"
      ]
    }
  }
}
```

**Key Points**:
- Uses **Python directly** (not PyInstaller executable)
- Simple configuration - just the Python script path
- Paths use double backslashes in JSON

### 5. Start ChimeraX

Before using the MCP server, ChimeraX must be running with the REST API enabled:

1. Launch ChimeraX
2. In the ChimeraX command line, type:
   ```
   remotecontrol rest start
   ```
3. You should see: `REST server started on port 50960`
4. Keep ChimeraX running

### 6. Restart Claude Desktop

Close Claude Desktop completely and reopen it.

### 7. Test the Server

In Claude Desktop, ask:
```
What ChimeraX tools do you have?
```

You should see a list of 15 molecular visualization tools.

**Example commands**:
```
Open PDB structure 1ubq in ChimeraX
Color it by chain and show as cartoon
Save a high-resolution image to protein.png
```

## Available Tools

The ChimeraX MCP server provides 15 tools:

1. **run_command** - Execute any ChimeraX command
2. **open_structure** - Open structures from PDB, AlphaFold, EMDB
3. **close_models** - Close models
4. **save_image** - Save high-quality images
5. **color_structure** - Color by chain, element, etc.
6. **show_style** - Change representation styles
7. **measure_distance** - Measure atomic distances
8. **align_structures** - Align multiple structures
9. **get_model_info** - Get model information
10. **show_surface** - Display molecular surfaces
11. **set_view** - Control camera
12. **select_residues** - Select specific residues
13. **find_clashes** - Find atomic clashes
14. **find_hbonds** - Find hydrogen bonds
15. **get_sequence** - Extract sequences

## Troubleshooting

### Error: "Cannot connect to ChimeraX"

**Solution**:
1. Ensure ChimeraX is running
2. Start the REST server: `remotecontrol rest start`
3. Check that port 50960 is not blocked by firewall

### Error: "No module named 'mcp'" or "No module named 'requests'"

**Solution**: Install the dependencies:
```bash
pip install mcp requests
```

### ChimeraX starts on a different port

**Solution**: Edit `chimerax_mcp_config.json` to match the port ChimeraX is using.

### Tools not showing in Claude Desktop

**Solution**:
1. Check Claude Desktop logs for errors
2. Verify the path in `claude_desktop_config.json` is correct
3. Ensure you restarted Claude Desktop after config changes

## Why Not PyInstaller?

We initially considered using PyInstaller to bundle the ChimeraX MCP Server into a standalone executable. However:

1. Python direct execution is simpler and more maintainable
2. No need to rebuild after changes
3. Easier to debug and modify
4. Works consistently across different Python versions

## Project Structure

```
chimerax-mcp/
├── chimerax_mcp_server.py      # Main MCP server script
├── chimerax_mcp_config.json    # Configuration (port)
├── requirements.txt            # Python dependencies
└── WINDOWS_SETUP.md           # This file
```

## How It Works

1. The MCP server communicates with Claude Desktop via stdio
2. The server sends HTTP requests to ChimeraX's REST API
3. ChimeraX executes commands and returns results
4. The server formats results and sends them back to Claude

## Notes

- ChimeraX must be running with REST API enabled before using the server
- The REST API runs locally (127.0.0.1) - no external access
- ChimeraX can be controlled both by Claude and manually during a session
- The server does not start or stop ChimeraX - you manage the ChimeraX process

## Version History

- **October 30, 2025**: Switched from PyInstaller to Python direct execution
- Successfully tested with Python 3.14 and ChimeraX on Windows 11
