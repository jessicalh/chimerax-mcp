@echo off
REM ChimeraX MCP Server - Windows Build Script
REM Alternative to Makefile for Windows systems

setlocal

set VERSION=1.1.0
set EXE_NAME=chimerax-mcp-server.exe
set DIST_DIR=dist
set BUILD_DIR=build

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="build" goto build
if "%1"=="clean" goto clean
if "%1"=="test" goto test
if "%1"=="installer" goto installer
if "%1"=="release" goto release
goto help

:help
echo ChimeraX MCP Server Build System
echo.
echo Available commands:
echo   build.bat build      - Build the executable
echo   build.bat test       - Run tests
echo   build.bat clean      - Clean build artifacts
echo   build.bat installer  - Create Windows installer
echo   build.bat release    - Full release build
echo.
goto end

:build
echo.
echo Building ChimeraX MCP Server executable...
echo.
if exist %DIST_DIR%\%EXE_NAME% del /F /Q %DIST_DIR%\%EXE_NAME%
pyinstaller chimerax_mcp_server.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    exit /b 1
)
echo.
echo [SUCCESS] Build complete! Executable: %DIST_DIR%\%EXE_NAME%
echo.
goto end

:test
echo.
echo Running tests...
echo.
python test_chimerax.py
if errorlevel 1 (
    echo.
    echo [ERROR] Tests failed!
    exit /b 1
)
echo.
echo [SUCCESS] All tests passed!
echo.
goto end

:clean
echo.
echo Cleaning build artifacts...
echo.
if exist %BUILD_DIR% rmdir /S /Q %BUILD_DIR%
if exist %DIST_DIR% rmdir /S /Q %DIST_DIR%
if exist __pycache__ rmdir /S /Q __pycache__
if exist Output rmdir /S /Q Output
del /F /Q *.pyc 2>nul
echo.
echo [SUCCESS] Clean complete!
echo.
goto end

:installer
echo.
echo Creating Windows installer...
echo.
if not exist %DIST_DIR%\%EXE_NAME% (
    echo [ERROR] Executable not found. Run 'build.bat build' first.
    exit /b 1
)

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    if errorlevel 1 (
        echo.
        echo [ERROR] Installer build failed!
        exit /b 1
    )
    echo.
    echo [SUCCESS] Installer created: Output\chimerax-mcp-setup.exe
    echo.
) else (
    echo [ERROR] Inno Setup not found!
    echo Please install from https://jrsoftware.org/isdl.php
    exit /b 1
)
goto end

:release
echo.
echo ========================================
echo Full Release Build
echo ========================================
echo.
call :clean
if errorlevel 1 exit /b 1

call :build
if errorlevel 1 exit /b 1

call :test
if errorlevel 1 exit /b 1

call :installer
if errorlevel 1 exit /b 1

echo.
echo ========================================
echo Release build complete!
echo ========================================
echo Executable: %DIST_DIR%\%EXE_NAME%
echo Installer:  Output\chimerax-mcp-setup.exe
echo.
echo Ready for distribution!
echo.
goto end

:end
endlocal
