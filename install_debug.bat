@echo off
echo ========================================
echo WebTalk - DEBUG Installation Script
echo ========================================
echo This version shows detailed output to help debug installation issues
echo.

REM Check if running as administrator
net session >nul 2>&1
if not %errorLevel% == 0 (
    echo WARNING: Some dependencies may require administrator privileges.
    echo If installation fails, please run as administrator.
    echo.
)

REM Check if Python is installed
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo ✓ Python found

REM Check Python version and details
python -c "import sys; print(f'Python {sys.version}'); print(f'Executable: {sys.executable}'); print(f'Platform: {sys.platform}')"

echo.
echo Creating virtual environment...
if exist whisper_env (
    echo Virtual environment already exists, removing old one...
    rmdir /s /q whisper_env
)

echo Running: python -m venv whisper_env
python -m venv whisper_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Error code: %errorlevel%
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo ✓ Virtual environment created successfully

echo.
echo Activating virtual environment...
echo Running: call whisper_env\Scripts\activate.bat
call whisper_env\Scripts\activate.bat

echo.
echo Testing virtual environment...
echo Current Python details:
python -c "import sys; print(f'Python: {sys.version}'); print(f'Executable: {sys.executable}'); print(f'Path: {sys.path[:3]}')"

echo.
echo Checking pip...
python -m pip --version

echo.
echo ========================================
echo Starting package installations...
echo ========================================

echo.
echo [1/6] Installing PyTorch with CUDA support...
echo Running: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118 --verbose
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118 --verbose
if errorlevel 1 (
    echo.
    echo WARNING: CUDA PyTorch installation failed (Error code: %errorlevel%)
    echo Trying CPU version...
    echo Running: pip install torch torchaudio --verbose
    pip install torch torchaudio --verbose
    if errorlevel 1 (
        echo ERROR: Failed to install PyTorch (Error code: %errorlevel%)
        echo This is a critical dependency - installation cannot continue
        echo.
        echo Press any key to exit...
        pause
        exit /b 1
    )
    echo ✓ PyTorch CPU version installed successfully
) else (
    echo ✓ PyTorch CUDA version installed successfully
)

echo.
echo [2/6] Installing OpenAI Whisper...
echo Running: pip install openai-whisper --verbose
pip install openai-whisper --verbose
if errorlevel 1 (
    echo ERROR: Failed to install OpenAI Whisper (Error code: %errorlevel%)
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)
echo ✓ OpenAI Whisper installed successfully

echo.
echo [3/6] Installing web framework dependencies...
echo Running: pip install fastapi uvicorn python-multipart requests pydantic --verbose
pip install fastapi uvicorn python-multipart requests pydantic --verbose
if errorlevel 1 (
    echo ERROR: Failed to install web dependencies (Error code: %errorlevel%)
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)
echo ✓ Web framework dependencies installed successfully

echo.
echo [4/6] Installing Flask for settings app...
echo Running: pip install flask --verbose
pip install flask --verbose
if errorlevel 1 (
    echo ERROR: Failed to install Flask (Error code: %errorlevel%)
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)
echo ✓ Flask installed successfully

echo.
echo [5/6] Installing PyWebView for GUI...
echo Running: pip install pywebview --verbose
pip install pywebview --verbose
if errorlevel 1 (
    echo WARNING: Failed to install PyWebView (Error code: %errorlevel%)
    echo The Settings GUI may not work properly
    echo You can still use the Chrome extension with the server
    echo.
) else (
    echo ✓ PyWebView installed successfully
)

echo.
echo [6/6] Installing additional dependencies...
echo Running: pip install psutil numpy sounddevice --verbose
pip install psutil numpy sounddevice --verbose
if errorlevel 1 (
    echo WARNING: Some optional dependencies failed to install (Error code: %errorlevel%)
    echo WebTalk should still work but some features may be limited
    echo.
)

echo.
echo Updating pip to latest version...
echo Running: python -m pip install --upgrade pip --verbose
python -m pip install --upgrade pip --verbose

echo.
echo Testing installations...
echo Testing PyTorch:
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

echo Testing Whisper:
python -c "import whisper; print('Whisper: OK')"

echo Testing FastAPI:
python -c "import fastapi; print('FastAPI: OK')"

echo Testing Flask:
python -c "import flask; print('Flask: OK')"

echo Testing PyWebView:
python -c "import webview; print('PyWebView: OK')" 2>nul || echo "PyWebView: Failed (Settings GUI may not work)"

echo.
echo ========================================
echo Installation Analysis Complete!
echo ========================================
echo.
echo If you see this message, the installation completed!
echo Any errors above will help identify what went wrong.
echo.
echo To start WebTalk:
echo   .\Launch.bat
echo.
echo DEBUG: Press any key to continue...
pause 