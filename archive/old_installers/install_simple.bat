@echo off
echo ========================================
echo WebTalk - Simple Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Creating virtual environment...

REM Remove existing environment if it exists
if exist "whisper_env" (
    echo Removing existing virtual environment...
    rmdir /s /q "whisper_env"
)

REM Create virtual environment
python -m venv whisper_env
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call whisper_env\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing core dependencies first...
pip install numpy==1.24.4
pip install pandas==2.0.3

echo Installing PyTorch with CUDA support...
pip install torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu118

echo Installing Whisper and other dependencies...
pip install openai-whisper
pip install fastapi uvicorn[standard]
pip install python-multipart aiofiles
pip install pydantic>=2.0.0
pip install soundfile librosa
pip install psutil
pip install requests

echo.
echo Testing installation...
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import whisper; print('Whisper imported successfully')"
python -c "import fastapi; print('FastAPI imported successfully')"

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo To start WebTalk:
echo 1. Run: launch_webtalk.bat (silent mode)
echo 2. Or run: run.bat (with terminal)
echo.
echo Then install the Chrome extension from the chrome_extension folder
echo.
pause 