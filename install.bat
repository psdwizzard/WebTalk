@echo off
echo ========================================
echo WebTalk - Simple Installation
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

REM Create virtual environment
python -m venv whisper_env
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call whisper_env\Scripts\activate.bat

echo Installing dependencies...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install openai-whisper
pip install fastapi uvicorn python-multipart requests pydantic
pip install flask pywebview

echo.
echo Testing installation...
python -c "import torch; print('PyTorch:', torch.__version__, 'CUDA:', torch.cuda.is_available())"
python -c "import whisper; print('Whisper: OK')"
python -c "import fastapi; print('FastAPI: OK')"
python -c "import flask; print('Flask: OK')"
python -c "import webview; print('PyWebView: OK')"

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo To start WebTalk:
echo 1. Run: run.bat (basic server)
echo 2. Or run: run_with_settings.bat (server + settings app)
echo 3. Install Chrome extension from chrome_extension folder
echo.
pause 