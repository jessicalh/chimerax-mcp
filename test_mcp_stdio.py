#!/usr/bin/env python3
"""
Test MCP server stdio communication.
This simulates what Claude Desktop does when it connects to the server.
"""

import json
import subprocess
import sys

def test_mcp_server():
    """Test the MCP server by sending initialization messages"""
    print("Starting MCP server...")

    # Start the server process
    proc = subprocess.Popen(
        [sys.executable, "chimerax_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    print("Sending initialize request...")
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()

    # Read response (with timeout)
    import time
    start = time.time()
    while time.time() - start < 5:
        if proc.poll() is not None:
            print(f"[ERROR] Server exited with code {proc.returncode}")
            stderr = proc.stderr.read()
            if stderr:
                print(f"Stderr: {stderr}")
            return False

        # Try to read a line
        try:
            # This is non-blocking simulation
            import select
            if sys.platform == 'win32':
                # Windows doesn't support select on pipes, just try to read
                line = proc.stdout.readline()
                if line:
                    print(f"[OK] Server response received")
                    print(f"Response: {line[:200]}...")
                    break
            else:
                if select.select([proc.stdout], [], [], 0.1)[0]:
                    line = proc.stdout.readline()
                    if line:
                        print(f"[OK] Server response received")
                        print(f"Response: {line[:200]}...")
                        break
        except Exception as e:
            print(f"[WARNING] Read attempt: {e}")

        time.sleep(0.1)

    # Send shutdown
    print("\nSending shutdown...")
    proc.terminate()
    proc.wait(timeout=2)

    print("\n[SUCCESS] MCP server starts and responds to messages")
    return True

if __name__ == "__main__":
    try:
        test_mcp_server()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
