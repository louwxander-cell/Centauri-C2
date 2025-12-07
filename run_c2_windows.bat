@echo off
REM TriAD C2 - Windows Launch Script
REM Double-click this file to run the application

echo ========================================
echo   TriAD C2 - Command and Control
echo ========================================
echo.

REM Change to script directory
cd /d %~dp0

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11+ from:
    echo https://www.python.org/downloads/windows/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python detected: 
python --version
echo.

REM Check if PySide6 is installed
python -c "import PySide6" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: PySide6 not found
    echo Installing dependencies...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting TriAD C2...
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

REM Run the application
python triad_c2.py

REM If application exits, pause so user can see any errors
echo.
echo ========================================
echo Application stopped
echo ========================================
pause
