# Port Detection Issue - Fixed

## What Was Wrong

The automatic port scanning was too slow and unreliable:
- Scanning took 60+ seconds in compiled executable
- Timeout-based detection didn't work well
- ChimeraX picks random ports, making it unreliable

## The Fix

Switched to a **configuration file approach**:

### 1. Configuration File

**File**: `chimerax_mcp_config.json` (installed with executable)

**Content**:
```json
{
  "chimerax_url": "http://127.0.0.1:50960",
  "timeout": 30,
  "auto_detect_port": false
}
```

**Location** (after install):
- All Users: `C:\Program Files\ChimeraX-MCP\chimerax_mcp_config.json`
- Current User: `%LOCALAPPDATA%\ChimeraX-MCP\chimerax_mcp_config.json`

### 2. Configuration Priority

The server checks in this order:
1. **Environment variable** `CHIMERAX_URL` (highest)
2. **Config file** `chimerax_mcp_config.json`
3. **Default** `http://127.0.0.1:50960`

### 3. ChimeraX Configuration

**To make ChimeraX always use port 50960:**

**In ChimeraX** → Favorites → Settings → Startup tab:

Add to "Execute these commands at startup":
```
remotecontrol rest start port 50960
```

Click "Save" and restart ChimeraX.

---

## How It Works Now

### Startup Sequence

1. User starts ChimeraX
2. ChimeraX auto-runs: `remotecontrol rest start port 50960`
3. User starts Claude Desktop
4. Claude loads MCP server
5. MCP server reads `chimerax_mcp_config.json`
6. MCP server connects to `http://127.0.0.1:50960`
7. Everything works!

**Startup time**: Instant (no scanning)

---

## For Users

### One-Time Setup

1. **Install** ChimeraX MCP Server (installer does this)
2. **Configure ChimeraX** to use port 50960 (one-time):
   - Settings → Startup → Add command: `remotecontrol rest start port 50960`
3. **Done!** Works forever after this

### If Using Different Port

Edit config file and ChimeraX startup command to match.

**Example for port 51000**:

**ChimeraX Startup**:
```
remotecontrol rest start port 51000
```

**Config File**:
```json
{
  "chimerax_url": "http://127.0.0.1:51000"
}
```

---

## What the Installer Includes

- ✅ `chimerax-mcp-server.exe` - Executable
- ✅ `chimerax_mcp_config.json` - Configuration (port 50960)
- ✅ `README.md` - Documentation
- ✅ `QUICKSTART.md` - Setup guide
- ✅ `update_claude_config.py` - Claude config updater

---

## Testing

```bash
# Test config loading
python -c "from chimerax_mcp_server import CHIMERAX_URL; print(CHIMERAX_URL)"
# Should print: http://127.0.0.1:50960
```

---

## Benefits of This Approach

✅ **Instant startup** - No port scanning
✅ **Reliable** - Known port, no guessing
✅ **User-configurable** - Simple JSON file
✅ **Environment override** - For advanced users
✅ **Simple** - One config file, one ChimeraX setting

---

## Documentation Updates

Added `CHIMERAX_SETUP.md` with complete instructions for:
- Setting ChimeraX to auto-start REST server
- Using a fixed port
- Configuring the MCP server
- Troubleshooting

---

## Status

✅ **Fixed and Tested**
✅ **Installer Updated**
✅ **Documentation Complete**
✅ **Ready for Distribution**
