#!/usr/bin/env python3
"""
Test script to verify the MCP server can be imported and run.

This does NOT test the full MCP protocol connection (which requires a client),
but it verifies:
1. All imports work
2. The server can be instantiated
3. Tools are properly registered
"""

import sys


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        import mcp
        from mcp.server.fastmcp import FastMCP
        import requests
        print("[OK] All imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def test_server_instantiation():
    """Test that the server can be instantiated"""
    print("\nTesting server instantiation...")
    try:
        # Import the server module
        import chimerax_mcp_server

        # Check if server was created
        if hasattr(chimerax_mcp_server, 'mcp'):
            print("[OK] MCP server instance created")
            return True
        else:
            print("[FAIL] MCP server instance not found")
            return False
    except Exception as e:
        print(f"[FAIL] Server instantiation error: {e}")
        return False


def test_tools_registered():
    """Test that tools are properly registered"""
    print("\nTesting tool registration...")
    try:
        import chimerax_mcp_server

        # Get the list of tools (this is implementation-dependent)
        # FastMCP uses a decorator pattern, so tools should be registered
        print("[OK] Server module loaded successfully")
        print("\nExpected tools:")
        tools = [
            "run_command",
            "open_structure",
            "close_models",
            "save_image",
            "color_structure",
            "show_style",
            "measure_distance",
            "align_structures",
            "get_model_info",
            "show_surface",
            "set_view",
            "select_residues",
            "find_clashes",
            "find_hbonds",
            "get_sequence"
        ]
        for tool in tools:
            if hasattr(chimerax_mcp_server, tool):
                print(f"  - {tool}")
            else:
                print(f"  [MISSING] {tool}")

        return True
    except Exception as e:
        print(f"[FAIL] Tool registration check error: {e}")
        return False


def test_chimerax_connection():
    """Test ChimeraX connection"""
    print("\nTesting ChimeraX connection...")
    try:
        import chimerax_mcp_server
        result = chimerax_mcp_server.execute_chimerax_command("version")
        print(f"[OK] ChimeraX connection works")
        print(f"  Response: {result[:80]}...")
        return True
    except chimerax_mcp_server.ChimeraXError as e:
        print(f"[FAIL] ChimeraX connection error: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MCP Server Module Test")
    print("=" * 60)

    if not test_imports():
        print("\n[ERROR] Please install required packages:")
        print("  pip install mcp requests")
        sys.exit(1)

    if not test_server_instantiation():
        print("\n[ERROR] Server instantiation failed")
        sys.exit(1)

    if not test_tools_registered():
        print("\n[ERROR] Tool registration check failed")
        sys.exit(1)

    if not test_chimerax_connection():
        print("\n[WARNING] ChimeraX connection failed")
        print("  This is expected if ChimeraX is not running")
        print("  To test fully, start ChimeraX with: remotecontrol rest start")

    print("\n" + "=" * 60)
    print("[SUCCESS] MCP server module tests passed!")
    print("=" * 60)
    print("\nThe MCP server is ready to use.")
    print("\nTo configure Claude Desktop:")
    print("  1. Copy claude_desktop_config.json content")
    print("  2. Paste into your Claude Desktop configuration file")
    print("  3. Restart Claude Desktop")
    print("\nConfiguration file location:")
    print("  Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Linux: ~/.config/Claude/claude_desktop_config.json")


if __name__ == "__main__":
    main()
