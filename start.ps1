# ==========================================
#  Water Management System - One-Click Start
#  Starts Flask API + React Frontend together
# ==========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Water Management System - Starting"    -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check we're in the right directory
if (-not (Test-Path "api.py")) {
    Write-Host "ERROR: Please run this from the project root where api.py is located." -ForegroundColor Red
    exit 1
}

# Activate venv if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "[1/3] No venv found, using system Python..." -ForegroundColor Yellow
}

# Start Flask Backend in a new minimized window
Write-Host "[2/3] Starting Flask API on port 5000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; python api.py" -WindowStyle Minimized

# Wait for backend
Write-Host "     Waiting for API to start..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start React Frontend in a new minimized window
Write-Host "[3/3] Starting React Frontend on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd '$PWD\frontend'; npm start" -WindowStyle Minimized

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Services Started!" -ForegroundColor Green
Write-Host ""
Write-Host "  Flask API:  http://localhost:5000/api" -ForegroundColor White
Write-Host "  React App:  http://localhost:3000"     -ForegroundColor White
Write-Host ""
Write-Host "  Both windows are minimized in taskbar." -ForegroundColor Gray
Write-Host "  Close them to stop the services."       -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Open browser after a short delay
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"
