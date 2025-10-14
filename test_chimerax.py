#!/usr/bin/env python3
"""
Test script for ChimeraX MCP Server

This script tests the ChimeraX REST API connection and basic functionality
before running the full MCP server.
"""

import requests
import sys

CHIMERAX_URL = "http://127.0.0.1:50960"


def test_connection():
    """Test if ChimeraX REST server is accessible"""
    print("Testing ChimeraX connection...")
    try:
        response = requests.get(f"{CHIMERAX_URL}/run?command=version", timeout=5)
        response.raise_for_status()
        print(f"[OK] Connected to ChimeraX")
        print(f"  Response: {response.text.strip()}")
        return True
    except requests.exceptions.ConnectionError:
        print("[FAIL] Cannot connect to ChimeraX")
        print("  Please ensure:")
        print("  1. ChimeraX is running")
        print("  2. REST server is enabled: 'remotecontrol rest start'")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_basic_commands():
    """Test basic ChimeraX commands"""
    print("\nTesting basic commands...")

    tests = [
        ("version", "Get version"),
        ("usage open", "Get open command usage"),
    ]

    for cmd, desc in tests:
        try:
            response = requests.get(
                f"{CHIMERAX_URL}/run?command={cmd.replace(' ', '+')}", timeout=10
            )
            response.raise_for_status()
            print(f"[OK] {desc}")
            if response.text.strip():
                # Print first line of response
                first_line = response.text.strip().split('\n')[0]
                print(f"  {first_line[:80]}...")
        except Exception as e:
            print(f"[FAIL] {desc}: {e}")
            return False

    return True


def test_structure_operations():
    """Test structure opening and manipulation"""
    print("\nTesting structure operations...")

    # Test opening a structure
    print("Testing: Open structure from PDB...")
    try:
        response = requests.get(
            f"{CHIMERAX_URL}/run?command=open+1ubq+from+pdb", timeout=30
        )
        response.raise_for_status()
        print("[OK] Structure opened successfully")

        # Get model info
        response = requests.get(
            f"{CHIMERAX_URL}/run?command=info+models", timeout=10
        )
        print(f"  Models: {response.text.strip()[:100]}...")

        # Test coloring
        print("Testing: Color by chain...")
        response = requests.get(
            f"{CHIMERAX_URL}/run?command=color+bychain", timeout=10
        )
        print("[OK] Colored by chain")

        # Close the model
        print("Testing: Close model...")
        response = requests.get(
            f"{CHIMERAX_URL}/run?command=close", timeout=10
        )
        print("[OK] Model closed")

        return True
    except Exception as e:
        print(f"[FAIL] Structure operation failed: {e}")
        return False


def test_mcp_imports():
    """Test if required Python packages are installed"""
    print("\nTesting Python dependencies...")

    try:
        import mcp
        print("[OK] mcp package installed")
    except ImportError:
        print("[FAIL] mcp package not found")
        print("  Install with: pip install mcp")
        return False

    try:
        import requests
        print("[OK] requests package installed")
    except ImportError:
        print("[FAIL] requests package not found")
        print("  Install with: pip install requests")
        return False

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("ChimeraX MCP Server Test Suite")
    print("=" * 60)

    # Test Python dependencies
    if not test_mcp_imports():
        print("\n⚠ Please install missing dependencies")
        sys.exit(1)

    # Test ChimeraX connection
    if not test_connection():
        print("\n⚠ Please start ChimeraX with REST server enabled")
        sys.exit(1)

    # Test basic commands
    if not test_basic_commands():
        print("\n⚠ Basic command tests failed")
        sys.exit(1)

    # Test structure operations
    if not test_structure_operations():
        print("\n⚠ Structure operation tests failed")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("[SUCCESS] All tests passed!")
    print("=" * 60)
    print("\nYou can now run the MCP server:")
    print("  python chimerax_mcp_server.py")
    print("\nOr configure Claude Desktop with the server.")


if __name__ == "__main__":
    main()
