#!/usr/bin/env python3
"""Test the standalone executable"""

import subprocess
import json
import sys
import time

def test_executable():
    """Test the chimerax-mcp-server.exe"""
    print("Testing standalone executable...")

    exe_path = r"C:\Users\jessi\trying\dist\chimerax-mcp-server.exe"

    # Start the executable
    proc = subprocess.Popen(
        [exe_path],
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

    # Read response
    start = time.time()
    while time.time() - start < 5:
        if proc.poll() is not None:
            print(f"[ERROR] Executable exited with code {proc.returncode}")
            stderr = proc.stderr.read()
            if stderr:
                print(f"Stderr: {stderr}")
            return False

        line = proc.stdout.readline()
        if line:
            print(f"[OK] Executable responded successfully")
            print(f"Response preview: {line[:150]}...")

            # Cleanup
            proc.terminate()
            proc.wait(timeout=2)
            print("\n[SUCCESS] Standalone executable works!")
            return True

        time.sleep(0.1)

    print("[ERROR] No response received within timeout")
    proc.terminate()
    return False

if __name__ == "__main__":
    try:
        success = test_executable()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
