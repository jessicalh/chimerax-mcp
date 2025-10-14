# Building ChimeraX MCP Server

Complete guide to building and distributing the ChimeraX MCP Server.

## Prerequisites

### Required
- **Python 3.10+** with pip
- **PyInstaller** (`pip install pyinstaller`)
- **Git** (for versioning)

### Optional (for installer)
- **Inno Setup 6** - Download from https://jrsoftware.org/isdl.php

## Quick Build

###Windows
```cmd
build.bat build
```

### Unix/Linux/macOS (using Makefile)
```bash
make build
```

## Build Commands

### Windows (`build.bat`)

```cmd
build.bat build      # Build executable only
build.bat test       # Run tests
build.bat clean      # Clean build artifacts
build.bat installer  # Create Windows installer (requires Inno Setup)
build.bat release    # Full release: clean, build, test, installer
```

### Unix/Linux/macOS (`Makefile`)

```bash
make build      # Build executable
make test       # Run tests
make clean      # Clean artifacts
make installer  # Create installer (Windows only)
make release    # Full release build
make all        # Clean + build + test
```

## Build System Components

### 1. Source Code
- `chimerax_mcp_server.py` - Main MCP server implementation
- **Auto-port detection**: Finds ChimeraX automatically
- **Optimized for compilation**: Fast startup in executable form

### 2. PyInstaller Configuration
- `chimerax_mcp_server.spec` - Build specification
- **Single-file executable**: All dependencies bundled
- **Size**: ~43 MB (includes Python runtime + dependencies)

### 3. Configuration Updater
- `update_claude_config.py` - Updates Claude Desktop config
- **Safe updates**: Backs up existing config
- **No duplicates**: Checks for existing entries
- **Preserves other servers**: Doesn't affect other MCP servers

### 4. Windows Installer
- `installer.iss` - Inno Setup script
- **Automatic Claude config update**: Runs during installation
- **Proper uninstall**: Clean removal
- **Upgrade support**: Handles version updates

## Manual Build Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Build Executable

```bash
pyinstaller chimerax_mcp_server.spec --clean --noconfirm
```

Output: `dist/chimerax-mcp-server.exe`

### 3. Test Executable

```bash
python test_chimerax.py
```

### 4. Create Installer (Windows only)

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Output: `Output/chimerax-mcp-setup.exe`

## Build Optimization

### Port Detection Performance

The executable uses optimized port detection:

1. **Fast path**: Tries port 50960 first (default) - instant if found
2. **Common ports**: Checks nearby ports sequentially
3. **Limited scan**: Only scans small range if needed
4. **50ms timeout**: Quick checks to avoid delays

**Expected startup:**
- Default port 50960: <100ms
- Non-default port: <500ms
- Worst case: <2 seconds

### Reducing Build Time

- **Use `--noconfirm`**: Skips confirmation prompts
- **Avoid `--clean`**: Only clean when dependencies change
- **Parallel builds**: Not supported by PyInstaller

### Reducing Executable Size

Current optimizations in `chimerax_mcp_server.spec`:
- **UPX compression**: Enabled (reduces ~10%)
- **Exclude unused modules**: Already optimized
- **Single file**: No external dependencies

Potential optimizations (not implemented):
- Strip debug symbols
- Exclude standard library modules
- Use lighter HTTP client

## Distribution

### For End Users

**Recommended**: Use the Windows installer
- Installs to `C:\Program Files\ChimeraX-MCP\`
- Automatically configures Claude Desktop
- Creates Start Menu shortcuts
- Handles upgrades

### For Developers

**Recommended**: Use Python version
- Faster startup
- Easier to modify
- No rebuild needed for changes
- Just need: `pip install mcp requests`

### Direct EXE Distribution

If distributing the EXE directly:

1. **Build** the executable
2. **Test** with ChimeraX running
3. **Package** with documentation:
   ```
   ChimeraX-MCP/
   ├── chimerax-mcp-server.exe
   ├── README.md
   ├── QUICKSTART.md
   └── LICENSE
   ```
4. **Distribute** as ZIP file

### Creating a GitHub Release

```bash
# Tag the version
git tag v1.1.0
git push --tags

# Create release with gh CLI
gh release create v1.1.0 \
  --title "ChimeraX MCP Server v1.1.0" \
  --notes "See CHANGELOG.md for details" \
  dist/chimerax-mcp-server.exe \
  Output/chimerax-mcp-setup.exe
```

## Testing

### Test Suite

```bash
# Test ChimeraX connection
python test_chimerax.py

# Test MCP server module
python test_mcp_server.py

# Test complete workflow
python full_integration_test.py
```

### Testing Executable

```bash
# Quick test
echo {"jsonrpc":"2.0","id":1,"method":"initialize"} | dist\chimerax-mcp-server.exe

# Full test
python test_executable.py
```

### Testing Installer

1. **Build installer**: `build.bat installer`
2. **Run installer**: `Output\chimerax-mcp-setup.exe`
3. **Verify installation**:
   - Check: `C:\Program Files\ChimeraX-MCP\chimerax-mcp-server.exe`
   - Check: `%APPDATA%\Claude\claude_desktop_config.json`
4. **Test with Claude Desktop**
5. **Uninstall** and verify cleanup

## Continuous Integration

### GitHub Actions (example)

```yaml
name: Build

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: build.bat build
      - run: build.bat test
      - uses: actions/upload-artifact@v3
        with:
          name: chimerax-mcp-server
          path: dist/chimerax-mcp-server.exe
```

## Troubleshooting

### Build Fails

**Problem**: PyInstaller not found
```
Solution: pip install pyinstaller
```

**Problem**: Import errors during build
```
Solution: pip install -r requirements.txt
```

**Problem**: File permission errors
```
Solution: Close any running instances of the executable
```

### Executable Doesn't Start

**Problem**: DLL load failures
```
Check: Requires 64-bit Windows 10/11
Solution: Install Visual C++ Redistributables
```

**Problem**: Takes too long to start
```
Cause: ChimeraX not on default port
Solution: Set CHIMERAX_URL environment variable
```

### Installer Fails

**Problem**: Inno Setup not found
```
Solution: Install from https://jrsoftware.org/isdl.php
```

**Problem**: Python not found during install
```
Note: Config update requires Python
Solution: Install Python or configure manually
```

## Version Management

### Updating Version Number

Update in these files:
1. `installer.iss` - Line 6: `#define MyAppVersion "X.Y.Z"`
2. `Makefile` - Line 11: `VERSION = X.Y.Z`
3. `build.bat` - Line 5: `set VERSION=X.Y.Z`
4. `pyproject.toml` - Line 7: `version = "X.Y.Z"`

### Version Scheme

- **Major (X)**: Breaking changes
- **Minor (Y)**: New features
- **Patch (Z)**: Bug fixes

Current version: **1.1.0**

## Advanced Topics

### Custom Build Options

Edit `chimerax_mcp_server.spec`:

```python
# Disable console window
console=False

# Add icon
icon='icon.ico'

# Exclude modules
excludes=['tkinter', 'matplotlib']
```

### Building for Other Platforms

**macOS**:
```bash
make build  # Creates .app bundle
```

**Linux**:
```bash
make build  # Creates ELF binary
```

Note: Installer is Windows-only

### Code Signing (Windows)

For enterprise distribution:

```bash
signtool sign /f certificate.pfx /p password dist\chimerax-mcp-server.exe
```

## Support

- **Build issues**: Check this guide
- **Runtime issues**: See README.md
- **Deployment**: See DEPLOYMENT.md

---

**Note**: Always test builds with a running ChimeraX instance before distributing!
