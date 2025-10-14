# ChimeraX MCP Server

A Model Context Protocol (MCP) server that connects Claude (and other AI assistants) to UCSF ChimeraX for molecular visualization and analysis.

## What This Does

This project lets you control ChimeraX through natural language conversations with Claude. Instead of typing commands manually, you can ask Claude to open structures, create visualizations, analyze molecular properties, and generate publication-quality images—all through simple conversation.

## Why This Exists

ChimeraX is powerful but has a learning curve. AI assistants like Claude are great at understanding intent but can't directly control scientific software. This bridge connects them, making molecular visualization more accessible through natural language.

## Features

- **15 specialized tools** for molecular visualization and analysis
- **No Python required** on deployment machines (standalone executable available)
- **Direct integration** with ChimeraX REST API
- **Works with Claude Desktop** via the Model Context Protocol
- **Simple setup** - configure once, use everywhere

### Available Tools

1. **Structure Loading**: Open from PDB, AlphaFold, EMDB, or local files
2. **Visualization**: Color by chain/element, change representations (cartoon, stick, surface)
3. **Analysis**: Find H-bonds, detect clashes, measure distances, align structures
4. **Output**: Save high-resolution images with custom settings
5. **Utility**: Select residues, control camera, manage models

Full tool list: `run_command`, `open_structure`, `close_models`, `save_image`, `color_structure`, `show_style`, `measure_distance`, `align_structures`, `get_model_info`, `show_surface`, `set_view`, `select_residues`, `find_clashes`, `find_hbonds`, `get_sequence`

## Quick Start

### Prerequisites

- UCSF ChimeraX (1.0+)
- Claude Desktop
- Windows 10/11 (64-bit) for executable, or Python 3.10+ for script version

### Installation (5 minutes)

#### Option A: Standalone Executable (Recommended)

1. **Download** `chimerax-mcp-server.exe` from releases
2. **Place** it somewhere permanent (e.g., `C:\Program Files\ChimeraX-MCP\`)
3. **Start ChimeraX** and enable REST server:
   ```
   remotecontrol rest start
   ```
4. **Configure Claude Desktop** (`%APPDATA%\Claude\claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "chimerax": {
         "command": "C:\\Program Files\\ChimeraX-MCP\\chimerax-mcp-server.exe"
       }
     }
   }
   ```
5. **Restart Claude Desktop**

#### Option B: Python Script

1. **Install dependencies**:
   ```bash
   pip install mcp requests
   ```
2. **Download** `chimerax_mcp_server.py`
3. **Start ChimeraX** with REST server enabled
4. **Configure Claude Desktop**:
   ```json
   {
     "mcpServers": {
       "chimerax": {
         "command": "python",
         "args": ["C:\\path\\to\\chimerax_mcp_server.py"]
       }
     }
   }
   ```
5. **Restart Claude Desktop**

### First Steps

Ask Claude:
```
What ChimeraX tools do you have access to?
```

Then try:
```
Open PDB structure 1ubq and show it as a cartoon colored by chain
```

## How It Works

```
You (natural language)
    ↓
Claude Desktop (AI reasoning)
    ↓
MCP Protocol (structured tool calls)
    ↓
ChimeraX MCP Server (command translation)
    ↓
ChimeraX REST API (execution)
    ↓
ChimeraX (visualization)
```

The server translates AI tool calls into ChimeraX commands and returns results back to Claude for natural language presentation.

## Example Workflows

### Basic Visualization
```
"Open PDB 1ubq, color it by chain, show as cartoon, and save a 4K image"
```

### Structural Analysis
```
"Load 1ubq and find all hydrogen bonds between helices"
```

### Comparison
```
"Open 1ubq and 1ubi, align them, and color the first one red and the second blue"
```

### Complex Workflow
```
"Open the AlphaFold prediction for human p53, show the high-confidence regions
as cartoon and low-confidence as transparent surface, then save an image"
```

## Project Structure

```
chimerax-mcp/
├── chimerax_mcp_server.py       # Main MCP server (570 lines)
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Package configuration
├── chimerax_mcp_server.spec    # PyInstaller build spec
├── README.md                   # This file
├── QUICKSTART.md              # Quick start guide
├── API_DESIGN.md              # Architecture documentation
├── DEPLOYMENT.md              # Deployment guide
└── tests/                     # Test suite
    ├── test_chimerax.py
    ├── test_mcp_server.py
    └── full_integration_test.py
```

## Building from Source

### Building the Executable

```bash
pip install pyinstaller mcp requests
pyinstaller chimerax_mcp_server.spec --clean
```

Output: `dist/chimerax-mcp-server.exe` (~43 MB)

### Running Tests

```bash
# Ensure ChimeraX is running with REST server enabled
python test_chimerax.py           # Test ChimeraX connection
python test_mcp_server.py         # Test MCP server module
python full_integration_test.py   # Test complete workflow
```

All tests should pass if ChimeraX is running properly.

## Configuration

### ChimeraX Setup

In ChimeraX command line:
```
remotecontrol rest start
```

Default port: 50960. If using a different port, edit `CHIMERAX_URL` in the source before building.

### Claude Desktop Setup

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

## Troubleshooting

### "Cannot connect to ChimeraX"
- Ensure ChimeraX is running
- Start REST server: `remotecontrol rest start`
- Check port 50960 is available

### Claude doesn't see tools
- Verify config file path is correct
- Check JSON syntax
- Use double backslashes in Windows paths
- Restart Claude Desktop completely

### Executable won't run
- Run as Administrator if needed
- Click "More info" → "Run anyway" on SmartScreen warning
- Ensure 64-bit Windows

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.

## Architecture

**Language**: Python 3.10+
**Framework**: FastMCP (official MCP SDK)
**Protocol**: MCP over stdio (JSON-RPC 2.0)
**ChimeraX Interface**: REST API (HTTP)
**Packaging**: PyInstaller for standalone distribution

The server is stateless and handles one command at a time. Each tool wraps ChimeraX commands with proper error handling and user-friendly responses.

See [API_DESIGN.md](API_DESIGN.md) for detailed architecture documentation.

## Limitations

- **Windows only** for the executable (Python version works cross-platform)
- **Local ChimeraX** only (must run on the same machine)
- **Single instance** (one ChimeraX per MCP server)
- **Synchronous** operations only (no parallel commands)
- **No authentication** (localhost only, relies on OS security)

## Future Enhancements

Potential additions (contributions welcome):
- Animation and movie creation tools
- Volume data visualization
- Molecular dynamics trajectory support
- Session management (save/load)
- Remote ChimeraX support
- Advanced analysis tools (SASA, interfaces, etc.)
- Cross-platform executable builds

## Contributing

This project welcomes contributions. Areas that could use help:
- Cross-platform testing (macOS, Linux)
- Additional ChimeraX tools
- Documentation improvements
- Bug fixes and error handling
- Performance optimization

Please open issues for bugs or feature requests.

## Technical Details

### Dependencies

**Runtime**:
- `mcp>=0.1.0` - Model Context Protocol SDK
- `requests>=2.31.0` - HTTP client

**Build**:
- `pyinstaller>=6.0.0` - Executable packaging

**ChimeraX**:
- Version 1.0+ with REST API support

### Performance

- Server startup: <1 second
- Command execution: 50-500ms (depends on ChimeraX)
- Structure loading: 2-5 seconds (network dependent)
- Image export: 1-2 seconds

### Security

- All communication is local (127.0.0.1)
- No external network access
- No file system access beyond ChimeraX capabilities
- 30-second timeout on all operations
- No shell command execution

## Acknowledgments

- **UCSF RBVI** for ChimeraX and its REST API
- **Anthropic** for Claude and the MCP specification
- **MCP team** for the Python SDK and FastMCP

## References

- [ChimeraX Documentation](https://www.cgl.ucsf.edu/chimerax/docs/user/index.html)
- [ChimeraX Remote Control](https://www.cgl.ucsf.edu/chimerax/docs/user/commands/remotecontrol.html)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Support

- **Issues**: Please open GitHub issues for bugs or questions
- **ChimeraX Help**: See [ChimeraX documentation](https://www.cgl.ucsf.edu/chimerax/docs/)
- **MCP Help**: See [MCP documentation](https://modelcontextprotocol.io/)

## Version

Current version: 1.0.0

Released: October 2025

---

**Note**: This is an independent project and is not officially affiliated with UCSF, ChimeraX, or Anthropic. It's a community tool to bridge ChimeraX with AI assistants through the Model Context Protocol.

Built with the goal of making molecular visualization more accessible through natural language interaction.
