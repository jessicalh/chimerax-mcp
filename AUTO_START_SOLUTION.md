# ChimeraX Auto-Start Solution

## Implementation

The MCP server now **owns and manages ChimeraX**, starting it automatically when Claude Desktop launches.

---

## How It Works

### Automatic Startup Sequence

1. **User starts Claude Desktop**
2. **Claude Desktop starts MCP server** (our executable)
3. **MCP server checks** if ChimeraX is running on configured port
4. **If not running**: MCP server starts ChimeraX with `--cmd "remotecontrol rest start port 50960"`
5. **ChimeraX launches** with REST server already enabled
6. **Claude can immediately** use ChimeraX tools

**User does nothing** - ChimeraX starts automatically!

### When Claude Desktop Closes

- MCP server shuts down
- ChimeraX is terminated cleanly
- Next time Claude starts, fresh ChimeraX session

---

## Configuration

### Config File: `chimerax_mcp_config.json`

```json
{
  "chimerax_url": "http://127.0.0.1:50960",
  "chimerax_port": 50960,
  "timeout": 30,
  "auto_start_chimerax": true,
  "chimerax_path": ""
}
```

**Parameters**:
- `chimerax_url` - Full REST API URL
- `chimerax_port` - Port number for REST server
- `auto_start_chimerax` - true = auto-start, false = manual start
- `chimerax_path` - Custom ChimeraX location (empty = auto-detect)
- `timeout` - Command timeout in seconds

### ChimeraX Auto-Detection

Server checks these locations automatically:
- `C:\Program Files\ChimeraX\bin\ChimeraX.exe`
- `C:\Program Files (x86)\ChimeraX\bin\ChimeraX.exe`
- `%LOCALAPPDATA%\UCSF ChimeraX\bin\ChimeraX.exe`
- `C:\Program Files\UCSF ChimeraX\bin\ChimeraX.exe`

### Custom ChimeraX Location

If ChimeraX is in a non-standard location, edit config:

```json
{
  "chimerax_path": "D:\\My Programs\\ChimeraX\\bin\\ChimeraX.exe"
}
```

---

## User Experience

### Before (Old Way)
1. Start ChimeraX manually
2. Type `remotecontrol rest start`
3. Start Claude Desktop
4. Use ChimeraX tools

### After (New Way)
1. **Start Claude Desktop**
2. **Use ChimeraX tools immediately**

ChimeraX starts automatically in the background!

---

## Command-Line Details

**How ChimeraX is Started**:
```cmd
ChimeraX.exe --cmd "remotecontrol rest start port 50960"
```

**What this does**:
- `--cmd` = Run command after startup
- `remotecontrol rest start port 50960` = Enable REST API on port 50960

**Process Management**:
- ChimeraX runs as child process of MCP server
- Server waits up to 10 seconds for REST server to respond
- Server terminates ChimeraX when it shuts down

---

## Benefits

✅ **Zero user configuration** - Just install and go
✅ **Automatic lifecycle** - ChimeraX starts/stops with Claude
✅ **Fixed port** - Always uses configured port
✅ **Clean shutdown** - No orphaned ChimeraX processes
✅ **Error recovery** - Falls back if ChimeraX already running

---

## Advanced Options

### Disable Auto-Start

If users want to manage ChimeraX manually:

Edit `chimerax_mcp_config.json`:
```json
{
  "auto_start_chimerax": false
}
```

Then start ChimeraX manually before using Claude.

### Different Port

Change both port settings:
```json
{
  "chimerax_url": "http://127.0.0.1:51000",
  "chimerax_port": 51000
}
```

### Multiple ChimeraX Instances

Each MCP server instance can manage its own ChimeraX:
- Instance 1: Port 50960
- Instance 2: Port 50961
- etc.

---

## Troubleshooting

### ChimeraX Doesn't Start

**Check**:
- ChimeraX installed in standard location?
- Set `chimerax_path` in config if custom location
- Verify user has permission to run ChimeraX

**Error Messages**:
Look in Claude Desktop logs for:
- "ChimeraX not found"
- "ChimeraX started successfully on port XXXX"
- "Error starting ChimeraX: ..."

### ChimeraX Starts But Can't Connect

**Wait a few seconds** - ChimeraX takes 5-10 seconds to fully start

**Check port** - Verify config file has correct port

**Check firewall** - Ensure localhost communication allowed

### Orphaned ChimeraX Processes

If MCP server crashes, ChimeraX may keep running.

**Close manually**:
- Close ChimeraX window, or
- Task Manager → End ChimeraX process

---

## Implementation Details

### Startup Wait Logic

```python
# Server tries for 10 seconds (50 attempts × 200ms)
for i in range(50):
    time.sleep(0.2)
    try:
        response = requests.get(url + "/run?command=version", timeout=0.5)
        if "ChimeraX" in response.text:
            # Success!
            break
    except:
        pass  # Keep trying
```

### Process Management

- **Windows**: Uses `CREATE_NEW_PROCESS_GROUP` for clean separation
- **Cleanup**: Terminates ChimeraX when MCP server exits
- **Timeout**: 5 seconds for graceful shutdown

---

## Distribution Impact

### Installer Changes

✅ Includes updated config with `auto_start_chimerax: true`
✅ No user configuration needed
✅ Works out of the box

### User Instructions

**Old**: "Start ChimeraX, then type commands, then use Claude"

**New**: "Use Claude - ChimeraX starts automatically"

---

## Testing

```bash
# Test auto-start
python chimerax_mcp_server.py
# Should start ChimeraX automatically

# Test with config disabled
# Edit config: "auto_start_chimerax": false
python chimerax_mcp_server.py
# Should wait for manual ChimeraX start
```

---

**ChimeraX is now owned by Claude Desktop - starts automatically, managed completely!**
