# Audio Classification Middleware - Quick Start
# PowerShell Script

Write-Host "Audio Classification Middleware - Quick Start" -ForegroundColor Cyan
Write-Host ("=" * 60)

# Check if we're in the right directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "Error: requirements.txt not found. Make sure you're in the backend directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Error: Virtual environment not found." -ForegroundColor Red
    Write-Host "Please run start_server_fixed.bat first to set up the environment." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow

# Try different activation methods
$activationScript = "venv\Scripts\Activate.ps1"
if (Test-Path $activationScript) {
    try {
        & $activationScript
        Write-Host "Virtual environment activated successfully." -ForegroundColor Green
    }
    catch {
        Write-Host "PowerShell activation failed, trying alternative method..." -ForegroundColor Yellow
        # Alternative method
        $env:VIRTUAL_ENV = "$(Get-Location)\venv"
        $env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"
    }
} else {
    Write-Host "PowerShell activation script not found, using alternative method..." -ForegroundColor Yellow
    $env:VIRTUAL_ENV = "$(Get-Location)\venv"
    $env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"
}

# Test imports
Write-Host "Testing dependencies..." -ForegroundColor Yellow

$testScript = @'
try:
    import fastapi, uvicorn, torch, torchaudio, librosa, sklearn, pandas, numpy, lightgbm, xgboost
    print("All dependencies available!")
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)
'@

python -c $testScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependencies not properly installed." -ForegroundColor Red
    Write-Host "Please run start_server_fixed.bat to install dependencies." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Test custom modules
Write-Host "Testing custom modules..." -ForegroundColor Yellow

$moduleTestScript = @'
try:
    from feature_extraction import AudioPreprocessor, extract_features_enhanced
    from model_manager import ModelLoader, AudioClassifier
    print("Custom modules available!")
except ImportError as e:
    print(f"Custom module error: {e}")
    exit(1)
'@

python -c $moduleTestScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "Custom modules not working properly." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check models directory
if (-not (Test-Path "..\ml_models")) {
    Write-Host "Warning: Models directory not found at ..\ml_models" -ForegroundColor Yellow
    Write-Host "The server will start but models will not be loaded." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
} else {
    Write-Host "Models directory found" -ForegroundColor Green
}

# Start the server
Write-Host ""
Write-Host "Starting Audio Classification Server..." -ForegroundColor Green
Write-Host ("=" * 60)
Write-Host "API Endpoint:       http://localhost:8000" -ForegroundColor Cyan
Write-Host "Test Interface:     test_interface.html" -ForegroundColor Cyan
Write-Host "WebSocket Client:   websocket_client.html" -ForegroundColor Cyan
Write-Host "Health Check:       http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "API Documentation:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python main.py

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
