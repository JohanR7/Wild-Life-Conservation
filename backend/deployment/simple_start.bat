@echo off
title Audio Classification Server - Simple Start
color 0A

echo.
echo Audio Classification Middleware - Simple Start
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found.
    echo Please run start_server_fixed.bat first to set up the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Test if activation worked
python -c "import sys; print('Virtual environment:', 'venv' in sys.executable)"

REM Test basic imports
echo Testing dependencies...
python -c "import fastapi, uvicorn; print('Core dependencies OK')"
if errorlevel 1 (
    echo ERROR: Core dependencies not found in virtual environment.
    echo Please run start_server_fixed.bat to install dependencies.
    pause
    exit /b 1
)

REM Test our modules
echo Testing custom modules...
python -c "from feature_extraction import extract_features_enhanced; from model_manager import ModelLoader; print('Custom modules OK')"
if errorlevel 1 (
    echo ERROR: Custom modules not working.
    pause
    exit /b 1
)

REM Check models directory
if not exist "..\ml_models" (
    echo WARNING: Models directory not found at ..\ml_models
    echo The server will start but models will not be loaded.
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        exit /b 1
    )
) else (
    echo Models directory found.
)

REM Start the server
echo.
echo ============================================================
echo Starting Audio Classification Server...
echo ============================================================
echo.
echo API Endpoint:       http://localhost:8000
echo Test Interface:     test_interface.html
echo Health Check:       http://localhost:8000/health
echo API Documentation:  http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

echo.
echo Server stopped.
pause
