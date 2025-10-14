# ChimeraX MCP Server - Final Setup Guide

## Working Solution

Simple, reliable, and tested.

---

## What You Get

- **Standalone Windows installer**: `chimerax-mcp-setup.exe` (45 MB)
- **No Python required** on target machines
- **Automatic Claude Desktop configuration**
- **Simple port-based setup**

---

## How It Works

### Configuration

**Single config file**: `chimerax_mcp_config.json`
```json
{
  "port": 5900
}
```

That's it. Just the port number.

### ChimeraX Setup

Configure ChimeraX to start REST server on port 5900:

**In ChimeraX** → Favorites → Settings → Startup tab

Add to "Execute these commands at startup":
```
remotecontrol rest start port 5900
```

Click "Save" and restart ChimeraX.

**One-time setup** - works forever after this.

---

## Installation Process

### Installer Prompts

1. **Welcome** → Next
2. **License** (MIT) → I Agree
3. **Installation Mode**:
   - ○ Install for all users (requires admin) → `C:\Program Files\ChimeraX-MCP\`
   - ○ Install for current user only (no admin) → `%LOCALAPPDATA%\ChimeraX-MCP\`
4. **Port Configuration**:
   - REST server port: `5900` (default)
5. **Destination Folder**: Confirm or change
6. **Ready to Install** → Install
7. **Completing**:
   - ☑ Configure Claude Desktop (automatic)
   - ☑ View README (optional)
8. **Finish**

### What Gets Installed

```
Installation directory:
├── chimerax-mcp-server.exe     (43 MB) - MCP server executable
├── chimerax_mcp_config.json    (17 bytes) - Port configuration
├── update_claude_config.py     (4 KB) - Config updater script
├── README.md                   (11 KB) - Documentation
├── QUICKSTART.md              (5 KB) - Quick start guide
└── LICENSE                    (1 KB) - MIT License
```

### Automatic Claude Configuration

Installer updates: `%APPDATA%\Claude\claude_desktop_config.json`

Adds this entry (preserving existing servers):
```json
{
  "mcpServers": {
    "chimerax": {
      "command": "C:\\Program Files (x86)\\ChimeraX-MCP\\chimerax-mcp-server.exe"
    }
  }
}
```

---

## Usage

### After Installation

1. **Configure ChimeraX** (one-time):
   - Settings → Startup
   - Add: `remotecontrol rest start port 5900`
   - Save and restart ChimeraX

2. **Start ChimeraX** (must be running before using Claude)

3. **Restart Claude Desktop**

4. **Use Claude**:
   ```
   "What ChimeraX tools do you have?"
   "Open PDB structure 1ubq"
   "Color it by chain and save an image"
   ```

### Tools Available

15 specialized tools:
- `run_command` - Execute any ChimeraX command
- `open_structure` - Open from PDB, AlphaFold, EMDB, files
- `close_models` - Close models
- `save_image` - Save high-resolution images
- `color_structure` - Color by chain, element, etc.
- `show_style` - Cartoon, stick, sphere, surface
- `measure_distance` - Measure atomic distances
- `align_structures` - Align structures
- `get_model_info` - Get model information
- `show_surface` - Molecular surfaces
- `set_view` - Camera control
- `select_residues` - Residue selection
- `find_clashes` - Clash detection
- `find_hbonds` - Hydrogen bond analysis
- `get_sequence` - Extract sequences

---

## Configuration Options

### Environment Variable Override

Set `CHIMERAX_URL` to override config file:

```json
{
  "mcpServers": {
    "chimerax": {
      "command": "C:\\Program Files (x86)\\ChimeraX-MCP\\chimerax-mcp-server.exe",
      "env": {
        "CHIMERAX_URL": "http://127.0.0.1:5900"
      }
    }
  }
}
```

### Different Port

Edit the config file:
```json
{
  "port": 6000
}
```

Then configure ChimeraX to use the same port:
```
remotecontrol rest start port 6000
```

---

## Deployment

### For Distribution

**Single file**: `Output/chimerax-mcp-setup.exe`

**Requirements**:
- Windows 10/11 (64-bit)
- ChimeraX installed
- Claude Desktop installed

### For Users

1. Download installer
2. Run installer (follow prompts)
3. Configure ChimeraX startup (one-time)
4. Use with Claude

---

## Build System

### Build Commands

```cmd
build.bat build      # Build executable
build.bat installer  # Create installer
build.bat test       # Run tests
build.bat clean      # Clean artifacts
build.bat release    # Full release build
```

### Version

Current: **1.1.0**

---

## Troubleshooting

### Claude Desktop Shows "Disconnected"

**Check**:
1. ChimeraX is running
2. ChimeraX has REST server enabled: `remotecontrol rest start port 5900`
3. Port in config matches ChimeraX port
4. Restart Claude Desktop

### Tools Not Showing

**Check**:
1. Claude Desktop config file has correct path
2. Config file syntax is valid JSON
3. Restart Claude Desktop completely

### Different Port Needed

**Edit**: `C:\Program Files (x86)\ChimeraX-MCP\chimerax_mcp_config.json`

Change port number, then configure ChimeraX to match.

---

## Technical Details

**Communication**:
```
Claude Desktop → MCP Server → HTTP REST → ChimeraX
```

**Port**: 5900 (configurable)
**Protocol**: MCP over stdio, HTTP REST to ChimeraX
**Config**: Single JSON file with port number

---

## Summary

✅ **Simple**: One config file, one setting
✅ **Reliable**: Fixed port, no scanning
✅ **Fast**: Instant startup
✅ **Clean**: No unnecessary complexity
✅ **Tested**: Working installation

**Distribution file**: `Output/chimerax-mcp-setup.exe`

Ready for production use.
