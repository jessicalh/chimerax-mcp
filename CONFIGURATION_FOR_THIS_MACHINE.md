# Claude Desktop Configuration - FOR THIS MACHINE

## Quick Setup (Copy & Paste)

### Step 1: Locate Your Claude Desktop Config File

**Press Windows Key + R** and paste:
```
%APPDATA%\Claude\claude_desktop_config.json
```

This will open: `C:\Users\jessi\AppData\Roaming\Claude\claude_desktop_config.json`

---

### Step 2: Configuration to Use

**If the file is empty or doesn't exist, use this:**

```json
{
  "mcpServers": {
    "chimerax": {
      "command": "C:\\Users\\jessi\\trying\\dist\\chimerax-mcp-server.exe"
    }
  }
}
```

**If you already have other MCP servers, ADD this section:**

```json
{
  "mcpServers": {
    "your-existing-server": {
      "command": "...",
      "args": [...]
    },
    "chimerax": {
      "command": "C:\\Users\\jessi\\trying\\dist\\chimerax-mcp-server.exe"
    }
  }
}
```

---

### Step 3: Before Starting Claude

1. **Start ChimeraX**
2. **In ChimeraX command line, type:**
   ```
   remotecontrol rest start
   ```
3. **Keep ChimeraX running**

---

### Step 4: Restart Claude Desktop

- Close Claude Desktop completely (check system tray)
- Reopen Claude Desktop

---

### Step 5: Test It

In Claude, ask:
```
What ChimeraX tools do you have access to?
```

You should see a list of 15 tools.

Then try:
```
Open PDB structure 1ubq in ChimeraX and color it by chain
```

---

## Exact File Paths for This Machine

| Item | Path |
|------|------|
| **Executable** | `C:\Users\jessi\trying\dist\chimerax-mcp-server.exe` |
| **Claude Config** | `C:\Users\jessi\AppData\Roaming\Claude\claude_desktop_config.json` |
| **Source Code** | `C:\Users\jessi\trying\chimerax_mcp_server.py` |
| **Documentation** | `C:\Users\jessi\trying\README.md` |

---

## Alternative: Using Python Instead of Executable

If you prefer to use the Python version:

```json
{
  "mcpServers": {
    "chimerax": {
      "command": "python",
      "args": [
        "C:\\Users\\jessi\\trying\\chimerax_mcp_server.py"
      ]
    }
  }
}
```

**Advantages of Python version:**
- Easier to modify/debug
- Slightly faster startup
- Can see source code

**Advantages of Executable:**
- No Python dependency
- Single file deployment
- Works on any Windows machine

---

## Current Status

✅ Executable built: **43 MB**
✅ Tested and working
✅ Ready to use

---

## Quick Troubleshooting

**Problem**: Claude doesn't see ChimeraX tools
- Check the path in config has double backslashes: `\\`
- Restart Claude Desktop completely
- Validate JSON syntax

**Problem**: "Cannot connect to ChimeraX"
- Start ChimeraX
- Type: `remotecontrol rest start`
- Check port 50960 is available

**Problem**: Executable won't run
- Right-click → "Run as Administrator"
- Check Windows Defender didn't block it

---

## What's Next?

1. Copy the configuration above
2. Paste into your Claude Desktop config
3. Start ChimeraX with REST server
4. Restart Claude Desktop
5. Start using AI-powered molecular visualization!

---

**Need Help?** See:
- `README.md` - Full documentation
- `DEPLOYMENT.md` - Deployment guide
- `QUICKSTART.md` - Quick start guide
