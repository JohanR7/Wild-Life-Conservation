@echo off
echo Activating virtual environment and starting server...

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found. Please run start_server_fixed.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if activation worked
python -c "import sys; print('Virtual environment active:', 'venv' in sys.executable)"

REM Test imports first
echo Testing imports...
python -c "
try:
    import fastapi
    import uvicorn
    import torch
    import torchaudio
    import librosa
    import sklearn
    import pandas
    import numpy
    print('✅ All dependencies imported successfully!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if errorlevel 1 (
    echo Dependencies not properly installed in virtual environment.
    echo Please run start_server_fixed.bat first.
    pause
    exit /b 1
)

REM Start the server
echo Starting server...
python main.py

pause
