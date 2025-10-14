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
import json
from typing import Optional, Dict, Any
from urllib.parse import quote
from mcp.server.fastmcp import FastMCP
from pathlib import Path

# Initialize MCP server
mcp = FastMCP("ChimeraX")

# ChimeraX REST API configuration
CHIMERAX_URL = None  # Will be loaded from config


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config file.
    Looks for config file in same directory as executable.

    Returns:
        Configuration dictionary with port number
    """
    # Find config file - look in same directory as this script/executable
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(sys.executable).parent
    else:
        # Running as script
        app_dir = Path(__file__).parent

    config_file = app_dir / "chimerax_mcp_config.json"

    # Default configuration
    default_port = 5900

    # Try to load from file
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return {"port": config.get("port", default_port)}
        except Exception:
            pass

    return {"port": default_port}


def get_chimerax_url() -> str:
    """
    Get ChimeraX URL from environment or config file.

    Returns:
        ChimeraX REST API URL
    """
    # 1. Environment variable override (highest priority)
    env_url = os.getenv("CHIMERAX_URL")
    if env_url:
        return env_url

    # 2. Configuration file
    config = load_config()
    port = config.get("port", 5900)
    return f"http://127.0.0.1:{port}"


# Import sys for executable path detection
import sys

# Load ChimeraX URL from config
CHIMERAX_URL = get_chimerax_url()


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
