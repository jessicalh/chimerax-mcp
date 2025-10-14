# ChimeraX MCP Server - Quick Start Guide

Get started with the ChimeraX MCP Server in 5 minutes!

## Prerequisites

1. **UCSF ChimeraX** installed and running
2. **Python 3.10+** installed
3. **Claude Desktop** installed

## Step 1: Install Dependencies

```bash
pip install mcp requests
```

## Step 2: Start ChimeraX REST Server

1. Launch ChimeraX
2. In the ChimeraX command line, type:
   ```
   remotecontrol rest start
   ```
3. You should see: `REST server started on port 50960`

## Step 3: Test the Connection

```bash
python test_chimerax.py
```

You should see all tests pass with `[SUCCESS] All tests passed!`

## Step 4: Configure Claude Desktop

### Find your configuration file:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Edit the configuration:

Open the file and add the ChimeraX server configuration. If the file is empty or doesn't exist, create it with this content:

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

**Important**: Update the path to match your actual installation location!

- On Windows, use double backslashes: `C:\\Users\\...`
- On macOS/Linux, use forward slashes: `/Users/...` or `/home/...`

### If you already have other MCP servers configured:

Add the chimerax entry to your existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": [...]
    },
    "chimerax": {
      "command": "python",
      "args": [
        "C:\\Users\\jessi\\trying\\chimerax_mcp_server.py"
      ]
    }
  }
}
```

## Step 5: Restart Claude Desktop

Close and restart Claude Desktop completely for the changes to take effect.

## Step 6: Try It Out!

Start a new conversation with Claude and try these examples:

### Example 1: Check Available Tools
```
What ChimeraX tools do you have access to?
```

### Example 2: Open a Structure
```
Open PDB structure 1ubq in ChimeraX
```

### Example 3: Visualize
```
Open 1ubq, color it by chain, and show it as a cartoon
```

### Example 4: Create an Image
```
Save a high-resolution image of the current view to protein.png
```

### Example 5: Analysis
```
Find all hydrogen bonds in the structure
```

## Troubleshooting

### "Cannot connect to ChimeraX"

**Solution**: Make sure ChimeraX is running with REST server enabled:
```
remotecontrol rest start
```

### Claude doesn't see the ChimeraX tools

**Solution**:
1. Check that the path in `claude_desktop_config.json` is correct
2. Validate JSON syntax (use a JSON validator online)
3. Restart Claude Desktop completely
4. Check Claude Desktop logs for errors

### Wrong port number

If ChimeraX starts on a different port, edit `chimerax_mcp_server.py`:
```python
CHIMERAX_URL = "http://127.0.0.1:YOUR_PORT"
```

## Available Tools

The MCP server provides 15 tools:

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

## Example Workflows

### Basic Visualization
```
1. Open PDB 1ubq
2. Color it by chain
3. Show as cartoon
4. Save image to 1ubq.png
```

### Structural Analysis
```
1. Open PDB 1ubq
2. Find hydrogen bonds
3. Find clashes
4. Measure distance between residue 45 CA and residue 72 CA
```

### Comparison
```
1. Open PDB 1ubq as model #1
2. Open PDB 1ubi as model #2
3. Align model #2 to model #1
4. Color model #1 red
5. Color model #2 blue
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore [ChimeraX documentation](https://www.cgl.ucsf.edu/chimerax/docs/user/index.html)
- Try more complex workflows with Claude

## Support

- ChimeraX documentation: https://www.cgl.ucsf.edu/chimerax/docs/user/index.html
- MCP documentation: https://modelcontextprotocol.io/
- Issues: Open an issue on GitHub

## Tips for Best Results

1. **Be specific**: Provide clear instructions to Claude
2. **Use model IDs**: Specify which model to operate on (e.g., "#1", "#2")
3. **Check ChimeraX**: Keep ChimeraX visible to see results in real-time
4. **Combine operations**: Ask Claude to perform multiple steps in sequence
5. **Save your work**: Ask Claude to save images or sessions

Happy molecular visualization with ChimeraX and Claude!
