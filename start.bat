@echo off
REM ==========================================
REM  Water Management System - One-Click Start
REM  Starts Flask API + React Frontend together
REM ==========================================

echo.
echo ========================================
echo   Water Management System - Starting
echo ========================================
echo.

REM Check we're in the right directory
if not exist "api.py" (
    echo ERROR: Please run this from the project root directory
    echo        where api.py is located.
    exit /b 1
)

REM Activate venv if it exists
if exist "venv\Scripts\activate.bat" (
    echo [1/3] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [1/3] No venv found, using system Python...
)

REM Start Flask Backend in background
echo [2/3] Starting Flask API on port 5000...
start "Flask API" /min cmd /c "python api.py"

REM Wait for backend to be ready
echo      Waiting for API to start...
timeout /t 3 /nobreak >nul

REM Start React Frontend
echo [3/3] Starting React Frontend on port 3000...
start "React Frontend" /min cmd /c "cd frontend && npm start"

echo.
echo ========================================
echo   Services Starting:
echo.
echo   Flask API:  http://localhost:5000/api
echo   React App:  http://localhost:3000
echo.
echo   Both windows are minimized in taskbar.
echo   Close them to stop the services.
echo ========================================
echo.

REM Open browser after a short delay
timeout /t 5 /nobreak >nul
start http://localhost:3000
