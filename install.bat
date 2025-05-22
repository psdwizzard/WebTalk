@echo off
echo Setting up WebTalk Whisper Environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv whisper_env

REM Activate virtual environment
echo Activating virtual environment...
call whisper_env\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install PyTorch with CUDA support (adjust for your CUDA version)
echo Installing PyTorch with CUDA support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Install Whisper and dependencies
echo Installing OpenAI Whisper...
pip install openai-whisper

REM Install additional dependencies for the API server
echo Installing additional dependencies...
pip install fastapi uvicorn python-multipart aiofiles

REM Install audio processing libraries
echo Installing audio processing libraries...
pip install soundfile librosa

REM Install Pillow for icon creation
echo Installing Pillow for icon creation...
pip install Pillow

REM Create placeholder icons
echo Creating placeholder icons...
python create_placeholder_icons.py

REM Test CUDA availability
echo Testing CUDA availability...
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA devices: {torch.cuda.device_count()}')"

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Install the Chrome extension from the 'chrome_extension' folder
echo 2. Run 'run.bat' to start the Whisper API server
echo 3. Right-click on any webpage to start recording!
echo.
pause 