@echo off
REM Start Backend Server (Windows)
REM Transport Delay Prediction API

echo Starting Backend Server...
echo.

cd backend

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH!
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env >nul 2>&1
)

REM Start the server
echo.
echo Starting FastAPI server on http://localhost:5000
echo API Documentation: http://localhost:5000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 5000

pause

