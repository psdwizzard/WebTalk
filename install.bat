@echo off
echo ========================================
echo WebTalk - Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo ✓ Python found. Creating virtual environment...

REM Create virtual environment
python -m venv whisper_env
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment created. Installing dependencies...
call whisper_env\Scripts\activate.bat

REM Install PyTorch with CUDA support
echo Installing PyTorch with CUDA support...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

REM Install other dependencies from requirements.txt
echo Installing WebTalk dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Testing Installation...
echo ========================================
python -c "import torch; print('✓ PyTorch:', torch.__version__, '- CUDA Available:', torch.cuda.is_available())"
python -c "import whisper; print('✓ Whisper: OK')"
python -c "import fastapi; print('✓ FastAPI: OK')"
python -c "import flask; print('✓ Flask: OK')"
python -c "import webview; print('✓ PyWebView: OK')"

echo.
echo ========================================
echo Installation Complete! 🎉
echo ========================================
echo.
echo To start WebTalk:
echo   .\Launch.bat
echo.
echo Then install the Chrome extension:
echo   1. Open Chrome and go to chrome://extensions/
echo   2. Enable "Developer mode"  
echo   3. Click "Load unpacked" and select the chrome_extension folder
echo.
echo You're ready to start transcribing!
echo.
pause 