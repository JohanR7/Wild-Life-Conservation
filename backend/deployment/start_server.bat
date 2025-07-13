@echo off
title Audio Classification Middleware Server
color 0A

echo.
echo ================================================================================
echo                    Audio Classification Middleware Server
echo ================================================================================
echo.

REM Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)
python --version

REM Check if we're in the backend directory
echo [2/6] Checking project structure...
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found. Make sure you're in the backend directory.
    pause
    exit /b 1
)
echo Project structure OK

REM Check if virtual environment exists, create if not
echo [3/6] Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo [4/6] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Check if models directory exists
echo [5/6] Checking models directory...
if not exist "..\ml_models" (
    echo [WARNING] Models directory not found at ..\ml_models
    echo Please ensure your trained models are in the correct location:
    echo   ml_models\gun_shots\
    echo     - scaler.pkl
    echo     - svm_model.pkl  
    echo     - xgboost_model.pkl
    echo   ml_models\wildlife\
    echo     - lightgbm_inat_overfitting.pkl
    echo     - rf_model_esc50.pkl
    echo     - xgboost_inat_overfitting.pkl
    echo     - xgboost_model_esc50.pkl
    echo.
    echo Do you want to continue anyway? (y/n)
    set /p continue="Answer: "
    if /i not "%continue%"=="y" (
        exit /b 1
    )
) else (
    echo Models directory found
)

REM Start the server
echo [6/6] Starting FastAPI server...
echo.
echo ================================================================================
echo                               SERVER INFORMATION
echo ================================================================================
echo.
echo  API Endpoint:       http://localhost:8000
echo  Test Interface:     test_interface.html (open in browser)
echo  WebSocket Client:   websocket_client.html (for real-time testing)
echo  Health Check:       http://localhost:8000/health
echo  API Documentation:  http://localhost:8000/docs
echo  Interactive API:    http://localhost:8000/redoc
echo.
echo ================================================================================
echo                                SERVER FEATURES
echo ================================================================================
echo.
echo  ✓ Process up to 5 audio files simultaneously
echo  ✓ Gunshot detection models (SVM, XGBoost)
echo  ✓ Wildlife classification models (LightGBM, Random Forest, XGBoost)
echo  ✓ Automatic best prediction selection
echo  ✓ WebSocket support for real-time processing
echo  ✓ REST API for integration
echo  ✓ Enhanced feature extraction (67 optimized features)
echo.
echo ================================================================================
echo.
echo Server starting... Press Ctrl+C to stop
echo.

python main.py

echo.
echo Server stopped.
pause
