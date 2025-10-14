@echo off
echo Testing executable startup time...
echo.
timeout /t 2 /nobreak >nul
echo { "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": { "protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": { "name": "test", "version": "1.0" } } } | dist\chimerax-mcp-server.exe
