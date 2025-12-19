@echo off
REM Start Frontend Server (Windows)
REM Transport Delay Prediction Frontend

echo Starting Frontend Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH!
    pause
    exit /b 1
)

REM Check if index.html exists
if not exist "index.html" (
    echo Error: index.html not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

set PORT=8000

echo Starting frontend server on http://localhost:%PORT%
echo Make sure backend is running on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python -m http.server %PORT%

pause

