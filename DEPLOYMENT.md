# ChimeraX MCP Server - Deployment Guide

## Standalone Executable Deployment

The ChimeraX MCP Server has been compiled into a standalone executable that **does not require Python** to be installed on the target machine.

---

## What Was Built

**File**: `dist/chimerax-mcp-server.exe`
**Size**: ~43 MB
**Type**: Standalone Windows executable (all dependencies bundled)
**Requirements**:
- Windows 10/11 (64-bit)
- ChimeraX installed and running

---

## For THIS Machine (Development Machine)

### Claude Desktop Configuration

**Location**: `%APPDATA%\Claude\claude_desktop_config.json`

**Full Path**: `C:\Users\jessi\AppData\Roaming\Claude\claude_desktop_config.json`

**Configuration**:
```json
{
  "mcpServers": {
    "chimerax": {
      "command": "C:\\Users\\jessi\\trying\\dist\\chimerax-mcp-server.exe"
    }
  }
}
```

**Important Notes**:
- Use double backslashes (`\\`) in the path
- No `args` needed - it's a single executable
- No Python installation required

---

## Deploying to Another Machine

### Option 1: Simple Deployment (Same Location)

1. **Copy the executable** to the same location on the target machine:
   ```
   C:\Users\<username>\trying\dist\chimerax-mcp-server.exe
   ```

2. **Install ChimeraX** on the target machine (if not already installed)

3. **Configure Claude Desktop** on the target machine:
   - Location: `%APPDATA%\Claude\claude_desktop_config.json`
   - Use the same configuration as above (update username if different)

4. **Start ChimeraX** and enable REST server:
   ```
   remotecontrol rest start
   ```

5. **Restart Claude Desktop**

### Option 2: Custom Location Deployment

1. **Copy the executable** to your preferred location:
   ```
   Example: C:\Program Files\ChimeraX-MCP\chimerax-mcp-server.exe
   ```

2. **Configure Claude Desktop** with the new path:
   ```json
   {
     "mcpServers": {
       "chimerax": {
         "command": "C:\\Program Files\\ChimeraX-MCP\\chimerax-mcp-server.exe"
       }
     }
   }
   ```

3. **Start ChimeraX** with REST server enabled

4. **Restart Claude Desktop**

### Option 3: Network Deployment

**For multiple users on a network:**

1. **Place executable on a network share**:
   ```
   \\server\shared\tools\chimerax-mcp-server.exe
   ```

2. **Users configure Claude Desktop**:
   ```json
   {
     "mcpServers": {
       "chimerax": {
         "command": "\\\\server\\shared\\tools\\chimerax-mcp-server.exe"
       }
     }
   }
   ```

---

## Distribution Package

### What to Include

Create a deployment package with:

```
ChimeraX-MCP-Server/
├── chimerax-mcp-server.exe    (43 MB - the executable)
├── README.md                   (User documentation)
├── QUICKSTART.md              (Quick start guide)
├── INSTALLATION.md            (This deployment guide)
└── claude_config_example.json (Example configuration)
```

### Creating the Distribution Package

```bash
# Create distribution folder
mkdir ChimeraX-MCP-Server-Dist
cd ChimeraX-MCP-Server-Dist

# Copy executable
copy ..\dist\chimerax-mcp-server.exe .

# Copy documentation
copy ..\README.md .
copy ..\QUICKSTART.md .
copy ..\DEPLOYMENT.md INSTALLATION.md

# Create example config
echo {
  "mcpServers": {
    "chimerax": {
      "command": "C:\\\\path\\\\to\\\\chimerax-mcp-server.exe"
    }
  }
} > claude_config_example.json

# Create ZIP for distribution
# (Use Windows Explorer or a tool like 7-Zip)
```

---

## Installation Instructions for End Users

### For Users Receiving the Executable

**Prerequisites:**
1. Windows 10/11 (64-bit)
2. UCSF ChimeraX installed
3. Claude Desktop installed

**Installation Steps:**

1. **Extract the package** to a location of your choice:
   - Recommended: `C:\Program Files\ChimeraX-MCP\`
   - Or: `C:\Tools\ChimeraX-MCP\`
   - Or: Any folder you prefer

2. **Start ChimeraX**:
   - Launch ChimeraX
   - In the command line, type: `remotecontrol rest start`
   - Keep ChimeraX running

3. **Configure Claude Desktop**:
   - Open: `%APPDATA%\Claude\claude_desktop_config.json`
   - If file doesn't exist, create it
   - Add this configuration (update path to where you placed the .exe):

   ```json
   {
     "mcpServers": {
       "chimerax": {
         "command": "C:\\Program Files\\ChimeraX-MCP\\chimerax-mcp-server.exe"
       }
     }
   }
   ```

   **Path Examples:**
   - Standard location: `"C:\\Program Files\\ChimeraX-MCP\\chimerax-mcp-server.exe"`
   - User location: `"C:\\Users\\YourName\\Tools\\chimerax-mcp-server.exe"`
   - Network share: `"\\\\server\\shared\\chimerax-mcp-server.exe"`

4. **Restart Claude Desktop**:
   - Completely close Claude Desktop (check system tray)
   - Reopen Claude Desktop

5. **Test the integration**:
   - Start a new conversation
   - Ask: "What ChimeraX tools do you have access to?"
   - Claude should list 15 tools

6. **Try it out**:
   - "Open PDB structure 1ubq in ChimeraX"
   - "Color it by chain and show as cartoon"

---

## Troubleshooting

### Executable Won't Run

**Error**: "This app can't run on your PC"
- **Solution**: Ensure you have 64-bit Windows
- **Solution**: Try running as Administrator

**Error**: "Windows protected your PC"
- **Solution**: Click "More info" → "Run anyway"
- (Executable is unsigned - expected for custom builds)

### Claude Doesn't See ChimeraX Tools

**Problem**: Tools not showing up

**Solutions**:
1. Verify the path in `claude_desktop_config.json` is correct
2. Check JSON syntax is valid (use jsonlint.com)
3. Ensure you used double backslashes (`\\`)
4. Restart Claude Desktop completely
5. Check Claude Desktop logs for errors

### Cannot Connect to ChimeraX

**Error**: "Cannot connect to ChimeraX"

**Solutions**:
1. Ensure ChimeraX is running
2. Start REST server in ChimeraX: `remotecontrol rest start`
3. Check port 50960 is not blocked by firewall
4. Verify ChimeraX version is 1.0+

### Different Port Number

If ChimeraX uses a different port:

**Option A**: Rebuild the executable (requires Python on dev machine)
- Edit `chimerax_mcp_server.py` line 28: `CHIMERAX_URL = "http://127.0.0.1:YOUR_PORT"`
- Rebuild with PyInstaller

**Option B**: Use Python version instead
- Install Python on target machine
- Use the Python script with environment variable

---

## Advanced: Environment Variables

The executable can be configured with environment variables if rebuilt with support:

```json
{
  "mcpServers": {
    "chimerax": {
      "command": "C:\\Program Files\\ChimeraX-MCP\\chimerax-mcp-server.exe",
      "env": {
        "CHIMERAX_URL": "http://127.0.0.1:60000"
      }
    }
  }
}
```

**Note**: Current build uses hardcoded port 50960. To enable environment variable support, modify the source before building.

---

## Comparison: Executable vs Python

| Feature | Standalone .exe | Python Script |
|---------|----------------|---------------|
| Python Required | ❌ No | ✅ Yes |
| Size | ~43 MB | ~50 KB (script only) |
| Dependencies | ✅ Bundled | ❌ Must install |
| Startup Time | ~1 second | ~0.5 seconds |
| Updates | Replace .exe | Edit script |
| Customization | Rebuild needed | Edit directly |
| Portability | ✅ High | ❌ Low |

**Recommendation**:
- **Use executable** for production deployment to end users
- **Use Python script** for development or customization

---

## Security Considerations

### Windows SmartScreen

First run may trigger Windows SmartScreen:
- This is normal for unsigned executables
- Click "More info" → "Run anyway"
- For enterprise deployment, consider code signing

### Firewall

The executable:
- Only connects to localhost (127.0.0.1)
- Does not accept incoming connections
- Does not require firewall exceptions
- ChimeraX REST server may need firewall exception

### Antivirus

Some antivirus software may flag:
- Packed executables (PyInstaller)
- Network connectivity
- Add exception if needed

---

## Building from Source

To rebuild the executable yourself:

```bash
# Install dependencies
pip install pyinstaller mcp requests

# Build
cd C:\Users\jessi\trying
pyinstaller chimerax_mcp_server.spec --clean

# Output: dist\chimerax-mcp-server.exe
```

**Build time**: ~45 seconds
**Output size**: ~43 MB

---

## Version Information

- **ChimeraX MCP Server**: 1.0.0
- **MCP Protocol**: 2024-11-05
- **Python**: 3.13 (used for building)
- **PyInstaller**: 6.16.0
- **Target OS**: Windows 10/11 (64-bit)

---

## Support

### For End Users

1. Check ChimeraX is running with REST server enabled
2. Verify Claude Desktop configuration path is correct
3. Restart both ChimeraX and Claude Desktop
4. See README.md for detailed troubleshooting

### For Developers

1. Source code: `chimerax_mcp_server.py`
2. Build spec: `chimerax_mcp_server.spec`
3. Test suite: `test_*.py` files
4. Documentation: `API_DESIGN.md`

---

## License

MIT License - Free to distribute and use

---

## Quick Reference Card

**For THIS Machine:**
```json
{
  "mcpServers": {
    "chimerax": {
      "command": "C:\\Users\\jessi\\trying\\dist\\chimerax-mcp-server.exe"
    }
  }
}
```

**Generic Template:**
```json
{
  "mcpServers": {
    "chimerax": {
      "command": "C:\\Path\\To\\chimerax-mcp-server.exe"
    }
  }
}
```

**Remember:**
1. Use double backslashes (`\\`)
2. Update path to actual location
3. Restart Claude Desktop after changes
4. Keep ChimeraX running with REST server enabled
