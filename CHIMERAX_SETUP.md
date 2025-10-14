# ChimeraX Configuration for MCP Server

## Problem

ChimeraX picks a random port each time it starts. The MCP server needs to know which port to connect to.

## Solution

Configure ChimeraX to always use the same port (50960) and auto-start the REST server.

---

## One-Time ChimeraX Setup

### Method 1: Using ChimeraX Preferences (Easiest)

1. **Start ChimeraX**

2. **Open Preferences**:
   - Menu: `Favorites` → `Settings...`
   - Or type: `settings`

3. **Go to Startup tab**

4. **In "Execute these commands at startup" field, add**:
   ```
   remotecontrol rest start port 50960
   ```

5. **Click "Save"**

6. **Restart ChimeraX** to verify it works

7. **Test**:
   - Open browser: `http://127.0.0.1:50960/cmdline.html`
   - You should see the ChimeraX command line interface

### Method 2: Using Startup Directory (Advanced)

1. **Create startup directory** (if it doesn't exist):
   ```
   C:\Users\<YourName>\chimerax_start\
   ```

2. **Create file**: `C:\Users\<YourName>\chimerax_start\rest_server.py`

3. **Add this content**:
   ```python
   # Auto-start REST server on port 50960
   from chimerax.core.commands import run
   run(session, "remotecontrol rest start port 50960")
   ```

4. **Restart ChimeraX**

### Method 3: Command-Line Shortcut

1. **Right-click ChimeraX shortcut** → Properties

2. **In "Target" field, add**:
   ```
   "C:\Program Files\ChimeraX\bin\ChimeraX.exe" --cmd "remotecontrol rest start port 50960"
   ```

3. **Click OK**

4. **Use this shortcut** to start ChimeraX

---

## Verifying It Works

After setup, when you start ChimeraX:

1. **Check ChimeraX log** (bottom of window):
   ```
   REST server started on port 50960
   ```

2. **Test with curl**:
   ```cmd
   curl http://127.0.0.1:50960/run?command=version
   ```

   Should return:
   ```
   UCSF ChimeraX version: X.X.X
   ```

3. **Test with browser**:
   - Open: http://127.0.0.1:50960/cmdline.html
   - Should show web command interface

---

## Using a Different Port

If you need to use a different port (e.g., 50961):

### 1. Configure ChimeraX

In ChimeraX startup preferences:
```
remotecontrol rest start port 50961
```

### 2. Update MCP Server Config

Edit: `C:\Program Files\ChimeraX-MCP\chimerax_mcp_config.json`

```json
{
  "chimerax_url": "http://127.0.0.1:50961",
  "timeout": 30,
  "auto_detect_port": false
}
```

### 3. Restart Claude Desktop

The MCP server will now use port 50961.

---

## Configuration File Location

**After Installation**:
- All Users: `C:\Program Files\ChimeraX-MCP\chimerax_mcp_config.json`
- Current User: `C:\Users\<name>\AppData\Local\ChimeraX-MCP\chimerax_mcp_config.json`

**Configuration Options**:
```json
{
  "chimerax_url": "http://127.0.0.1:50960",
  "timeout": 30,
  "auto_detect_port": false
}
```

**Parameters**:
- `chimerax_url` - Full URL to ChimeraX REST API
- `timeout` - Command timeout in seconds (default: 30)
- `auto_detect_port` - Reserved for future use (keep false)

---

## Priority Order

The MCP server checks for ChimeraX URL in this order:

1. **Environment variable** `CHIMERAX_URL` (highest priority)
2. **Config file** `chimerax_mcp_config.json`
3. **Default** `http://127.0.0.1:50960`

---

## Troubleshooting

### ChimeraX REST Server Not Starting

**Check ChimeraX log** for errors:
- Port already in use → Choose different port
- Permission denied → Run as administrator

**Verify command syntax**:
```
remotecontrol rest start port 50960
```

### MCP Server Can't Connect

**Check config file**:
- Location correct?
- JSON syntax valid?
- Port matches ChimeraX?

**Test manually**:
```cmd
curl http://127.0.0.1:50960/run?command=version
```

### Port Already in Use

**Find what's using the port**:
```cmd
netstat -ano | findstr :50960
```

**Choose a different port**:
- Update ChimeraX startup: `remotecontrol rest start port 50961`
- Update config file: `"chimerax_url": "http://127.0.0.1:50961"`

---

## Recommended Setup

**Best Practice**:

1. **ChimeraX**: Always start REST server on port 50960
2. **MCP Config**: Use default (50960)
3. **No changes needed** - just works!

**Setup ChimeraX once** using Preferences method above, then:
- ChimeraX auto-starts REST server every time
- MCP server finds it immediately
- No manual steps needed

---

## For Installer/Deployment

The installer includes `chimerax_mcp_config.json` with sensible defaults (port 50960).

Users just need to:
1. Run the installer
2. Configure ChimeraX startup (one-time)
3. Use it!

---

## Advanced: Dynamic Port (Not Recommended)

If ChimeraX must use random ports, you can set in config:
```json
{
  "auto_detect_port": true
}
```

**Note**: This is slow and unreliable. Better to configure ChimeraX to use a fixed port.
