#!/usr/bin/env python3
"""
ChimeraX MCP Server

This Model Context Protocol (MCP) server provides AI assistants with access to
UCSF ChimeraX molecular visualization capabilities. It enables Claude and other
LLMs to control ChimeraX for tasks like:
- Opening and visualizing molecular structures
- Performing structural analysis
- Creating publication-quality images
- Measuring molecular properties
- Aligning and comparing structures

Prerequisites:
- ChimeraX must be running with remote control enabled
- Start ChimeraX REST server: `remotecontrol rest start`
"""

import requests
import os
from typing import Optional, Dict, Any
from urllib.parse import quote
from mcp.server.fastmcp import FastMCP
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize MCP server
mcp = FastMCP("ChimeraX")

# ChimeraX REST API configuration
CHIMERAX_URL = None  # Will be auto-detected


def find_chimerax_port() -> Optional[str]:
    """
    Auto-detect ChimeraX REST API port by scanning localhost.

    Returns:
        URL string like "http://127.0.0.1:50960" or None if not found
    """
    # First check environment variable override
    env_url = os.getenv("CHIMERAX_URL")
    if env_url:
        return env_url

    # Try default port first (fast path - 99% of cases)
    default_port = 50960
    if check_chimerax_port(default_port):
        return f"http://127.0.0.1:{default_port}"

    # If not on default, try common nearby ports
    # ChimeraX typically uses ports in this range
    common_ports = [50961, 50962, 50959, 50958, 49152, 49153, 49154]

    for port in common_ports:
        if check_chimerax_port(port):
            return f"http://127.0.0.1:{port}"

    # Last resort: do a limited parallel scan
    # Only scan a small range to avoid long delays
    port_range = list(range(50963, 51000))

    batch_size = 5
    for i in range(0, len(port_range), batch_size):
        batch = port_range[i:i+batch_size]
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = {executor.submit(check_chimerax_port, port): port for port in batch}
            for future in as_completed(futures):
                port = futures[future]
                if future.result():
                    return f"http://127.0.0.1:{port}"

    return None


def check_chimerax_port(port: int, timeout: float = 0.05) -> bool:
    """
    Check if ChimeraX REST server is running on given port.

    Args:
        port: Port number to check
        timeout: Connection timeout in seconds

    Returns:
        True if ChimeraX is responding on this port
    """
    try:
        # First check if port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()

        if result != 0:
            return False

        # Port is open, verify it's ChimeraX by sending version command
        url = f"http://127.0.0.1:{port}/run?command=version"
        response = requests.get(url, timeout=timeout)

        # Check if response contains ChimeraX signature
        if response.status_code == 200 and "ChimeraX" in response.text:
            return True

    except (socket.error, requests.RequestException):
        pass

    return False


# Auto-detect ChimeraX port on startup
CHIMERAX_URL = find_chimerax_port()

if CHIMERAX_URL is None:
    # Will fail gracefully on first command with helpful error message
    CHIMERAX_URL = "http://127.0.0.1:50960"  # Fallback for error messages


class ChimeraXError(Exception):
    """Custom exception for ChimeraX communication errors"""
    pass


def execute_chimerax_command(command: str) -> str:
    """
    Execute a command in ChimeraX via REST API.

    Args:
        command: ChimeraX command to execute

    Returns:
        Response text from ChimeraX

    Raises:
        ChimeraXError: If command execution fails
    """
    try:
        # URL encode the command
        encoded_command = quote(command)
        url = f"{CHIMERAX_URL}/run?command={encoded_command}"

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        return response.text.strip()
    except requests.exceptions.ConnectionError:
        raise ChimeraXError(
            "Cannot connect to ChimeraX. Please ensure ChimeraX is running "
            "and the REST server is enabled with 'remotecontrol rest start'"
        )
    except requests.exceptions.Timeout:
        raise ChimeraXError("ChimeraX command timed out after 30 seconds")
    except requests.exceptions.RequestException as e:
        raise ChimeraXError(f"Error communicating with ChimeraX: {str(e)}")


@mcp.tool()
def run_command(command: str) -> str:
    """
    Execute any ChimeraX command directly.

    This is the most flexible tool - it allows execution of any valid ChimeraX
    command. Use this for advanced operations or commands not covered by other tools.

    Args:
        command: Any valid ChimeraX command (e.g., "open 1ubq", "color red", "save image.png")

    Returns:
        Output from ChimeraX command execution

    Examples:
        - run_command("version")
        - run_command("open 1ubq from pdb")
        - run_command("color #1 bychain")
    """
    try:
        result = execute_chimerax_command(command)
        return result if result else "Command executed successfully (no output)"
    except ChimeraXError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def open_structure(
    identifier: str,
    source: str = "pdb",
    format: Optional[str] = None,
    model_id: Optional[str] = None
) -> str:
    """
    Open a molecular structure in ChimeraX.

    Args:
        identifier: Structure identifier (PDB ID, UniProt ID, file path, etc.)
        source: Data source - 'pdb', 'alphafold', 'emdb', 'file', or 'local'
        format: File format (only needed for local files, e.g., 'pdb', 'mmcif', 'mol2')
        model_id: Optional model ID to assign (e.g., "#1", "#2")

    Returns:
        Confirmation message with details about opened structure

    Examples:
        - open_structure("1ubq", "pdb")  # Open PDB structure
        - open_structure("P12345", "alphafold")  # Open AlphaFold prediction
        - open_structure("C:/path/to/file.pdb", "local", "pdb")  # Open local file
    """
    try:
        # Build open command based on source
        if source == "local" or source == "file":
            cmd = f"open {identifier}"
            if format:
                cmd += f" format {format}"
        else:
            cmd = f"open {identifier} from {source}"

        if model_id:
            cmd += f" id {model_id}"

        result = execute_chimerax_command(cmd)
        return result if result else f"Successfully opened {identifier} from {source}"
    except ChimeraXError as e:
        return f"Error opening structure: {str(e)}"


@mcp.tool()
def close_models(model_spec: str = "all") -> str:
    """
    Close molecular models in ChimeraX.

    Args:
        model_spec: Model specifier (e.g., "#1", "#1,2", "all")

    Returns:
        Confirmation message

    Examples:
        - close_models("#1")  # Close model 1
        - close_models("all")  # Close all models
    """
    try:
        cmd = f"close {model_spec}" if model_spec != "all" else "close"
        result = execute_chimerax_command(cmd)
        return result if result else f"Successfully closed {model_spec}"
    except ChimeraXError as e:
        return f"Error closing models: {str(e)}"


@mcp.tool()
def save_image(
    filepath: str,
    width: int = 1920,
    height: int = 1080,
    transparent_background: bool = False,
    supersample: int = 3
) -> str:
    """
    Save current ChimeraX visualization as an image.

    Args:
        filepath: Output file path (supports .png, .jpg, .tiff)
        width: Image width in pixels
        height: Image height in pixels
        transparent_background: Use transparent background
        supersample: Supersampling level for antialiasing (1-4, higher = better quality)

    Returns:
        Confirmation message with file path

    Examples:
        - save_image("protein.png", 3840, 2160)
        - save_image("figure.png", transparent_background=True)
    """
    try:
        cmd = f"save {filepath} width {width} height {height} supersample {supersample}"
        if transparent_background:
            cmd += " transparentBackground true"

        result = execute_chimerax_command(cmd)
        return f"Image saved to {filepath}" + (f"\n{result}" if result else "")
    except ChimeraXError as e:
        return f"Error saving image: {str(e)}"


@mcp.tool()
def color_structure(
    model_spec: str,
    color_scheme: str,
    target: str = "all"
) -> str:
    """
    Color molecular structures using various schemes.

    Args:
        model_spec: Model specifier (e.g., "#1", "#1,2", "all")
        color_scheme: Color scheme - 'bychain', 'byhetero', 'byelement', 'bypolymer',
                     'sequential', or specific color name (e.g., 'red', 'blue', '#FF0000')
        target: What to color - 'all', 'cartoons', 'atoms', 'surfaces'

    Returns:
        Confirmation message

    Examples:
        - color_structure("#1", "bychain")
        - color_structure("#1", "red", "cartoons")
        - color_structure("all", "byelement", "atoms")
    """
    try:
        if target == "all":
            cmd = f"color {model_spec} {color_scheme}"
        else:
            cmd = f"color {model_spec} {color_scheme} target {target}"

        result = execute_chimerax_command(cmd)
        return result if result else f"Successfully colored {model_spec} using {color_scheme}"
    except ChimeraXError as e:
        return f"Error coloring structure: {str(e)}"


@mcp.tool()
def show_style(
    model_spec: str,
    style: str = "cartoon",
    show: bool = True
) -> str:
    """
    Change molecular representation style.

    Args:
        model_spec: Model specifier (e.g., "#1", "#1:1-100")
        style: Display style - 'cartoon', 'stick', 'sphere', 'ball', 'surface'
        show: True to show, False to hide

    Returns:
        Confirmation message

    Examples:
        - show_style("#1", "cartoon")
        - show_style("#1:1-50", "stick")
        - show_style("#1", "atoms", False)  # Hide atoms
    """
    try:
        action = "show" if show else "hide"
        cmd = f"{action} {model_spec} {style}"

        result = execute_chimerax_command(cmd)
        return result if result else f"Successfully changed style for {model_spec}"
    except ChimeraXError as e:
        return f"Error changing style: {str(e)}"


@mcp.tool()
def measure_distance(
    atom1: str,
    atom2: str,
    model_spec: str = "#1"
) -> str:
    """
    Measure distance between two atoms.

    Args:
        atom1: First atom specifier (e.g., ":45@CA", ":45@CA")
        atom2: Second atom specifier
        model_spec: Model containing the atoms

    Returns:
        Distance in angstroms

    Examples:
        - measure_distance(":45@CA", ":72@CA")  # Distance between CA atoms
        - measure_distance(":100@NZ", ":150@OE1", "#1")
    """
    try:
        cmd = f"distance {model_spec}{atom1} {model_spec}{atom2}"
        result = execute_chimerax_command(cmd)
        return result if result else "Distance measured (check ChimeraX for result)"
    except ChimeraXError as e:
        return f"Error measuring distance: {str(e)}"


@mcp.tool()
def align_structures(
    mobile_spec: str,
    reference_spec: str,
    method: str = "matchmaker"
) -> str:
    """
    Align one structure to another.

    Args:
        mobile_spec: Model to move (e.g., "#2")
        reference_spec: Reference model (e.g., "#1")
        method: Alignment method - 'matchmaker' (sequence-based) or 'align' (current view)

    Returns:
        Alignment statistics (RMSD, etc.)

    Examples:
        - align_structures("#2", "#1")  # Align model 2 to model 1
        - align_structures("#2", "#1", "align")
    """
    try:
        if method == "matchmaker":
            cmd = f"matchmaker {mobile_spec} to {reference_spec}"
        else:
            cmd = f"align {mobile_spec} to {reference_spec}"

        result = execute_chimerax_command(cmd)
        return result if result else f"Successfully aligned {mobile_spec} to {reference_spec}"
    except ChimeraXError as e:
        return f"Error aligning structures: {str(e)}"


@mcp.tool()
def get_model_info(model_spec: str = "all") -> str:
    """
    Get information about loaded models.

    Args:
        model_spec: Model specifier (e.g., "#1", "all")

    Returns:
        Model information including atoms, residues, chains

    Examples:
        - get_model_info("#1")
        - get_model_info("all")
    """
    try:
        cmd = f"info models {model_spec}"
        result = execute_chimerax_command(cmd)
        return result if result else "No models loaded"
    except ChimeraXError as e:
        return f"Error getting model info: {str(e)}"


@mcp.tool()
def show_surface(
    model_spec: str,
    show: bool = True,
    transparency: int = 0,
    color: Optional[str] = None
) -> str:
    """
    Show or hide molecular surface.

    Args:
        model_spec: Model specifier
        show: True to show, False to hide
        transparency: Transparency level (0-100, 0=opaque, 100=fully transparent)
        color: Optional surface color

    Returns:
        Confirmation message

    Examples:
        - show_surface("#1")
        - show_surface("#1", transparency=50, color="blue")
        - show_surface("#1", show=False)  # Hide surface
    """
    try:
        if show:
            cmd = f"surface {model_spec}"
            if transparency > 0:
                cmd += f" transparency {transparency}"
            if color:
                execute_chimerax_command(cmd)
                cmd = f"color {model_spec} {color} target surfaces"
        else:
            cmd = f"surface {model_spec} hide"

        result = execute_chimerax_command(cmd)
        return result if result else f"Surface {'shown' if show else 'hidden'} for {model_spec}"
    except ChimeraXError as e:
        return f"Error with surface: {str(e)}"


@mcp.tool()
def set_view(
    view: str,
    model_spec: Optional[str] = None
) -> str:
    """
    Set the camera view.

    Args:
        view: View name - 'initial', 'front', 'back', 'top', 'bottom', 'left', 'right'
        model_spec: Optional model to center view on

    Returns:
        Confirmation message

    Examples:
        - set_view("initial")
        - set_view("front", "#1")
    """
    try:
        if view == "initial":
            cmd = "view"
        else:
            cmd = f"view {view}"

        if model_spec:
            execute_chimerax_command(f"view {model_spec}")
        else:
            result = execute_chimerax_command(cmd)
            return result if result else f"View set to {view}"
    except ChimeraXError as e:
        return f"Error setting view: {str(e)}"


@mcp.tool()
def select_residues(
    model_spec: str,
    residue_range: str,
    chain: Optional[str] = None
) -> str:
    """
    Select specific residues.

    Args:
        model_spec: Model specifier
        residue_range: Residue range (e.g., "1-50", "100", "45,72,91")
        chain: Optional chain ID

    Returns:
        Confirmation message

    Examples:
        - select_residues("#1", "1-50", "A")
        - select_residues("#1", "100,200,300")
    """
    try:
        spec = f"{model_spec}:{residue_range}"
        if chain:
            spec += f"/{chain}"

        cmd = f"select {spec}"
        result = execute_chimerax_command(cmd)
        return result if result else f"Selected residues {residue_range}"
    except ChimeraXError as e:
        return f"Error selecting residues: {str(e)}"


@mcp.tool()
def find_clashes(
    model_spec: str = "all",
    cutoff: float = 0.6,
    save_to_file: Optional[str] = None
) -> str:
    """
    Find atomic clashes (overlaps).

    Args:
        model_spec: Model specifier
        cutoff: Overlap cutoff in angstroms (negative = allowable overlap)
        save_to_file: Optional file path to save clash list

    Returns:
        List of clashes found

    Examples:
        - find_clashes("#1")
        - find_clashes("#1", cutoff=-0.4)
    """
    try:
        cmd = f"clashes {model_spec} overlapCutoff {cutoff}"
        if save_to_file:
            cmd += f" saveFile {save_to_file}"

        result = execute_chimerax_command(cmd)
        return result if result else "Clash analysis complete (check ChimeraX log)"
    except ChimeraXError as e:
        return f"Error finding clashes: {str(e)}"


@mcp.tool()
def find_hbonds(
    model_spec: str = "all",
    show_distances: bool = True,
    save_to_file: Optional[str] = None
) -> str:
    """
    Find hydrogen bonds.

    Args:
        model_spec: Model specifier
        show_distances: Show distance labels
        save_to_file: Optional file path to save H-bond list

    Returns:
        Hydrogen bond information

    Examples:
        - find_hbonds("#1")
        - find_hbonds("#1", save_to_file="hbonds.txt")
    """
    try:
        cmd = f"hbonds {model_spec}"
        if show_distances:
            cmd += " reveal true"
        if save_to_file:
            cmd += f" saveFile {save_to_file}"

        result = execute_chimerax_command(cmd)
        return result if result else "H-bond analysis complete"
    except ChimeraXError as e:
        return f"Error finding H-bonds: {str(e)}"


@mcp.tool()
def get_sequence(model_spec: str, chain: Optional[str] = None) -> str:
    """
    Get protein/nucleic acid sequence.

    Args:
        model_spec: Model specifier
        chain: Optional chain ID

    Returns:
        Sequence information

    Examples:
        - get_sequence("#1", "A")
        - get_sequence("#1")
    """
    try:
        spec = model_spec
        if chain:
            spec += f"/{chain}"

        cmd = f"sequence {spec}"
        result = execute_chimerax_command(cmd)
        return result if result else "Sequence viewer opened in ChimeraX"
    except ChimeraXError as e:
        return f"Error getting sequence: {str(e)}"


# Add resources for common molecular structures
@mcp.resource("pdb://{pdb_id}")
def get_pdb_info(pdb_id: str) -> str:
    """
    Get information about a PDB entry.
    Resource URI format: pdb://XXXX where XXXX is the PDB ID.
    """
    return f"PDB Entry: {pdb_id.upper()}\nUse open_structure('{pdb_id}', 'pdb') to load this structure."


@mcp.resource("alphafold://{uniprot_id}")
def get_alphafold_info(uniprot_id: str) -> str:
    """
    Get information about an AlphaFold prediction.
    Resource URI format: alphafold://PXXXXX where PXXXXX is the UniProt ID.
    """
    return f"AlphaFold Prediction: {uniprot_id.upper()}\nUse open_structure('{uniprot_id}', 'alphafold') to load this prediction."


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
