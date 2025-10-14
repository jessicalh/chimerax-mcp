# ChimeraX MCP Server - API Design Document

## Overview

This document describes the complete API design for the ChimeraX MCP (Model Context Protocol) server, including architectural decisions, tool design, and integration patterns.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                      User                                │
│              (Natural Language)                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Chat Interface
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Claude Desktop                              │
│         (LLM + MCP Client)                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ MCP Protocol (stdio)
                     │ JSON-RPC 2.0
                     ▼
┌─────────────────────────────────────────────────────────┐
│         ChimeraX MCP Server                              │
│         (Python + FastMCP)                               │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Tools (15)                                       │  │
│  │  - run_command                                    │  │
│  │  - open_structure                                 │  │
│  │  - save_image                                     │  │
│  │  - ...                                            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Resources (2)                                    │  │
│  │  - pdb://{pdb_id}                                │  │
│  │  - alphafold://{uniprot_id}                      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ChimeraX Client                                  │  │
│  │  - HTTP REST Client                               │  │
│  │  - Error Handling                                 │  │
│  │  - Command Encoding                               │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP REST API
                     │ GET /run?command=...
                     ▼
┌─────────────────────────────────────────────────────────┐
│           UCSF ChimeraX                                  │
│           (Desktop Application)                          │
│                                                          │
│  - Molecular Visualization                               │
│  - Structural Analysis                                   │
│  - Command Processing                                    │
│  - REST Server (port 50960)                             │
└─────────────────────────────────────────────────────────┘
```

### Communication Flow

1. **User → Claude**: Natural language request
2. **Claude → MCP Server**: Tool invocation via MCP protocol
3. **MCP Server → ChimeraX**: HTTP REST API call
4. **ChimeraX → MCP Server**: Command result (text)
5. **MCP Server → Claude**: Structured response
6. **Claude → User**: Natural language summary

## Design Decisions

### 1. Language Selection: Python

**Rationale:**
- Official MCP Python SDK with FastMCP
- Simple and idiomatic tool definition
- Native requests library for HTTP
- Easy deployment (single file)
- Strong typing support

**Alternatives Considered:**
- TypeScript: Official SDK but requires Node.js
- Go: No official SDK
- Rust: Steeper learning curve

### 2. Communication Protocol: REST API

**Rationale:**
- ChimeraX provides REST API out-of-the-box
- Simple HTTP GET requests
- No additional dependencies
- Cross-platform compatibility
- Easy to test with curl

**Alternatives Considered:**
- XML-RPC: More complex, requires Python client library
- Direct Python API: Would require ChimeraX Python environment
- WebSockets: Not supported by ChimeraX

### 3. Tool Design Philosophy

**Principles:**
1. **Layered abstraction**: Generic `run_command` + specialized tools
2. **Discoverable**: Clear names and descriptions
3. **Safe defaults**: Sensible parameter defaults
4. **Flexible**: Support both simple and advanced use cases
5. **Error-tolerant**: Graceful error handling

### 4. Error Handling Strategy

**Approach:**
- Custom `ChimeraXError` exception
- Try-catch in every tool
- User-friendly error messages
- Distinguish connection errors from command errors
- Never crash the MCP server

## Tool Catalog

### Core Tools

#### 1. run_command
**Purpose**: Execute any ChimeraX command
**Category**: Core/Generic
**Parameters**:
- `command` (str): Any valid ChimeraX command

**Design Notes**:
- Most flexible tool
- Fallback for unsupported operations
- Allows power users to use full ChimeraX API

#### 2. open_structure
**Purpose**: Open molecular structures
**Category**: Data Loading
**Parameters**:
- `identifier` (str): PDB ID, UniProt ID, or file path
- `source` (str): 'pdb', 'alphafold', 'emdb', 'file', 'local'
- `format` (Optional[str]): File format for local files
- `model_id` (Optional[str]): Assign specific model ID

**Design Notes**:
- Abstracts different data sources
- Supports both remote and local files
- Handles format detection

#### 3. save_image
**Purpose**: Save visualization as image
**Category**: Output
**Parameters**:
- `filepath` (str): Output path
- `width` (int): Width in pixels (default: 1920)
- `height` (int): Height in pixels (default: 1080)
- `transparent_background` (bool): Transparency (default: False)
- `supersample` (int): Anti-aliasing level 1-4 (default: 3)

**Design Notes**:
- Publication-quality defaults
- Support for transparency
- High DPI support via supersampling

### Visualization Tools

#### 4. color_structure
**Purpose**: Color molecules
**Category**: Visualization
**Parameters**:
- `model_spec` (str): Which model to color
- `color_scheme` (str): Coloring method
- `target` (str): What to color (default: 'all')

**Supported color schemes**:
- `bychain`: Color each chain differently
- `byelement`: Color by atomic element
- `byhetero`: Distinguish heteroatoms
- `bypolymer`: Color by polymer type
- Color names: 'red', 'blue', etc.
- Hex colors: '#FF0000'

#### 5. show_style
**Purpose**: Change molecular representation
**Category**: Visualization
**Parameters**:
- `model_spec` (str): Which model
- `style` (str): Display style (default: 'cartoon')
- `show` (bool): Show or hide (default: True)

**Supported styles**:
- `cartoon`: Ribbon/cartoon representation
- `stick`: Stick model
- `sphere`: Space-filling spheres
- `ball`: Ball-and-stick
- `surface`: Molecular surface

#### 6. show_surface
**Purpose**: Display molecular surfaces
**Category**: Visualization
**Parameters**:
- `model_spec` (str): Which model
- `show` (bool): Show or hide (default: True)
- `transparency` (int): 0-100 (default: 0)
- `color` (Optional[str]): Surface color

**Design Notes**:
- Separate from show_style for fine control
- Support for transparency critical for visualization
- Can color surface independently

### Analysis Tools

#### 7. measure_distance
**Purpose**: Measure atomic distances
**Category**: Analysis
**Parameters**:
- `atom1` (str): First atom specifier
- `atom2` (str): Second atom specifier
- `model_spec` (str): Model ID (default: '#1')

**Atom specifier format**: `:residue@atomname`
**Example**: `:45@CA` (residue 45, CA atom)

#### 8. align_structures
**Purpose**: Align structures
**Category**: Analysis
**Parameters**:
- `mobile_spec` (str): Structure to move
- `reference_spec` (str): Reference structure
- `method` (str): Alignment method (default: 'matchmaker')

**Supported methods**:
- `matchmaker`: Sequence-based alignment
- `align`: Spatial alignment

#### 9. find_clashes
**Purpose**: Find atomic clashes
**Category**: Analysis
**Parameters**:
- `model_spec` (str): Which model (default: 'all')
- `cutoff` (float): Overlap threshold (default: 0.6)
- `save_to_file` (Optional[str]): Save results

**Design Notes**:
- Negative cutoff allows some overlap
- File output for batch analysis

#### 10. find_hbonds
**Purpose**: Find hydrogen bonds
**Category**: Analysis
**Parameters**:
- `model_spec` (str): Which model (default: 'all')
- `show_distances` (bool): Show labels (default: True)
- `save_to_file` (Optional[str]): Save results

### Utility Tools

#### 11. close_models
**Purpose**: Close models
**Category**: Utility
**Parameters**:
- `model_spec` (str): Which models (default: 'all')

#### 12. get_model_info
**Purpose**: Get model information
**Category**: Utility
**Parameters**:
- `model_spec` (str): Which models (default: 'all')

#### 13. set_view
**Purpose**: Control camera
**Category**: Utility
**Parameters**:
- `view` (str): View name
- `model_spec` (Optional[str]): Center on model

**Supported views**:
- `initial`: Reset to initial view
- `front`, `back`, `top`, `bottom`, `left`, `right`

#### 14. select_residues
**Purpose**: Select residues
**Category**: Utility
**Parameters**:
- `model_spec` (str): Which model
- `residue_range` (str): Range specification
- `chain` (Optional[str]): Chain ID

**Range formats**:
- Single: `"100"`
- Range: `"1-50"`
- Multiple: `"45,72,91"`

#### 15. get_sequence
**Purpose**: Extract sequences
**Category**: Utility
**Parameters**:
- `model_spec` (str): Which model
- `chain` (Optional[str]): Chain ID

## Resources

### 1. pdb://{pdb_id}
**Purpose**: Reference PDB database entries
**Format**: `pdb://1UBQ`
**Returns**: Information about PDB entry

### 2. alphafold://{uniprot_id}
**Purpose**: Reference AlphaFold predictions
**Format**: `alphafold://P04637`
**Returns**: Information about AlphaFold prediction

**Design Notes**:
- Resources provide contextual information
- Don't execute commands
- Help LLM understand data sources

## ChimeraX Integration

### REST API Details

**Endpoint**: `http://127.0.0.1:50960/run`
**Method**: GET or POST
**Parameter**: `command` (URL-encoded ChimeraX command)
**Response**: Plain text output

### Command Encoding

```python
from urllib.parse import quote
encoded = quote("open 1ubq from pdb")
url = f"http://127.0.0.1:50960/run?command={encoded}"
```

### Error Handling

**Connection Errors**:
- ChimeraX not running
- REST server not started
- Wrong port number

**Command Errors**:
- Invalid command syntax
- Invalid model specifiers
- File not found

### Timeout Strategy

- Default: 30 seconds
- Structure loading may take longer
- Allow user to cancel via Claude

## MCP Protocol Details

### Transport

**Type**: stdio (standard input/output)
**Format**: JSON-RPC 2.0
**Messages**:
- Requests: Client → Server
- Responses: Server → Client
- Notifications: Bidirectional

### Tool Schema

Each tool is automatically serialized to JSON schema by FastMCP:

```json
{
  "name": "open_structure",
  "description": "Open a molecular structure in ChimeraX.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "identifier": {"type": "string"},
      "source": {"type": "string", "default": "pdb"},
      "format": {"type": "string"},
      "model_id": {"type": "string"}
    },
    "required": ["identifier"]
  }
}
```

### Resource Schema

```json
{
  "uri": "pdb://{pdb_id}",
  "name": "get_pdb_info",
  "description": "Get information about a PDB entry."
}
```

## Security Considerations

### Threat Model

**Threats**:
1. Malicious commands to ChimeraX
2. File system access via ChimeraX
3. Denial of service (long-running commands)

**Mitigations**:
1. ChimeraX runs in user context (sandboxed)
2. File operations limited to ChimeraX capabilities
3. 30-second timeout on all commands
4. No shell command execution (only ChimeraX commands)
5. Local-only communication (127.0.0.1)

### Input Validation

- URL encoding prevents injection
- Model specifiers validated by ChimeraX
- File paths handled by ChimeraX
- No shell metacharacters processed

## Performance Considerations

### Bottlenecks

1. **Network latency**: Minimal (localhost)
2. **ChimeraX processing**: Main bottleneck
3. **JSON serialization**: Negligible
4. **MCP protocol overhead**: Minimal

### Optimization Strategies

1. **Batch commands**: Use `run_command` for sequences
2. **Caching**: ChimeraX maintains model cache
3. **Async operations**: Not implemented (future work)

## Testing Strategy

### Unit Tests

- Tool parameter validation
- Command generation
- Error handling
- URL encoding

### Integration Tests

- ChimeraX connection
- Command execution
- Error scenarios
- Timeout handling

### End-to-End Tests

- Full MCP workflow
- Claude Desktop integration
- Real-world workflows

## Future Enhancements

### Potential Additions

1. **Animation tools**
   - `create_animation()`
   - `save_movie()`

2. **Volume data**
   - `load_volume()`
   - `show_isosurface()`

3. **MD simulation**
   - `load_trajectory()`
   - `animate_trajectory()`

4. **Batch operations**
   - `batch_process()`
   - Command queuing

5. **Session management**
   - `save_session()`
   - `load_session()`

6. **Advanced analysis**
   - `calculate_sasa()`
   - `find_interfaces()`

### Alternative Transports

- **XML-RPC**: For non-Python clients
- **WebSocket**: For real-time updates
- **Remote ChimeraX**: Network access

### Async Operations

- Long-running commands
- Progress reporting
- Cancellation support

## Lessons Learned

### What Worked Well

1. **FastMCP**: Excellent developer experience
2. **REST API**: Simple and reliable
3. **Type hints**: Clear interface definitions
4. **Error handling**: Robust and informative

### Challenges

1. **Resource syntax**: Initial confusion with URI templates
2. **Windows encoding**: Unicode issues with console output
3. **Documentation**: ChimeraX command reference scattered

### Best Practices

1. **Start simple**: Core functionality first
2. **Test incrementally**: Each component separately
3. **Document clearly**: Examples for every tool
4. **Handle errors gracefully**: Never crash
5. **Provide defaults**: Make tools easy to use

## References

- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [ChimeraX User Guide](https://www.cgl.ucsf.edu/chimerax/docs/user/index.html)
- [ChimeraX Remote Control](https://www.cgl.ucsf.edu/chimerax/docs/user/commands/remotecontrol.html)

## Conclusion

This ChimeraX MCP server provides a comprehensive, well-designed interface for AI assistants to control molecular visualization software. The architecture is extensible, the tools are practical, and the implementation is robust.

The layered approach—from generic command execution to specialized tools—provides both flexibility and ease of use. The integration with ChimeraX via REST API is simple yet powerful, and the MCP protocol enables natural language interaction through Claude.

This design serves as a template for building MCP servers for other scientific software applications.
