# ChimeraX MCP Server - Build System
# Makefile for Windows (requires Python and PyInstaller)

.PHONY: all clean build test installer help

# Configuration
PYTHON = python
PYINSTALLER = pyinstaller
SPEC_FILE = chimerax_mcp_server.spec
EXE_NAME = chimerax-mcp-server.exe
DIST_DIR = dist
BUILD_DIR = build
INSTALLER_SCRIPT = installer.iss
VERSION = 1.1.0

# Default target
all: clean build test

help:
	@echo ChimeraX MCP Server Build System
	@echo.
	@echo Available targets:
	@echo   make build      - Build the executable
	@echo   make test       - Run tests
	@echo   make installer  - Create Windows installer
	@echo   make clean      - Clean build artifacts
	@echo   make all        - Clean, build, and test
	@echo   make release    - Build and create installer
	@echo.

# Build the executable
build:
	@echo Building ChimeraX MCP Server executable...
	@if exist $(DIST_DIR)\$(EXE_NAME) del /F /Q $(DIST_DIR)\$(EXE_NAME)
	$(PYINSTALLER) $(SPEC_FILE) --clean --noconfirm
	@echo.
	@echo Build complete! Executable: $(DIST_DIR)\$(EXE_NAME)
	@echo.

# Run tests
test:
	@echo Running tests...
	$(PYTHON) test_chimerax.py
	@echo.
	@echo All tests passed!
	@echo.

# Build installer (requires Inno Setup)
installer: build
	@echo Creating Windows installer...
	@if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
		"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" $(INSTALLER_SCRIPT)
	) else (
		echo ERROR: Inno Setup not found!
		echo Please install from https://jrsoftware.org/isdl.php
		exit /b 1
	)
	@echo.
	@echo Installer created: Output\chimerax-mcp-setup.exe
	@echo.

# Clean build artifacts
clean:
	@echo Cleaning build artifacts...
	@if exist $(BUILD_DIR) rmdir /S /Q $(BUILD_DIR)
	@if exist $(DIST_DIR) rmdir /S /Q $(DIST_DIR)
	@if exist __pycache__ rmdir /S /Q __pycache__
	@if exist *.pyc del /F /Q *.pyc
	@if exist Output rmdir /S /Q Output
	@echo.
	@echo Clean complete!
	@echo.

# Full release build
release: clean build test installer
	@echo.
	@echo ========================================
	@echo Release build complete!
	@echo ========================================
	@echo Executable: $(DIST_DIR)\$(EXE_NAME)
	@echo Installer:  Output\chimerax-mcp-setup.exe
	@echo.
	@echo Ready for distribution!
	@echo.

# Quick rebuild (no clean)
rebuild:
	@echo Quick rebuilding...
	$(PYINSTALLER) $(SPEC_FILE) --noconfirm
	@echo Rebuild complete!
	@echo.

# Version bump
version:
	@echo Current version: $(VERSION)
	@echo Update VERSION variable in Makefile to change version
	@echo.
