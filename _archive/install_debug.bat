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
echo Running: call whisper_env\\Scripts\\activate.bat
call whisper_env\\Scripts\\activate.bat

echo.
echo Testing virtual environment activation...
REM This Python command will output its executable path. Note: CHCP 437 is sometimes needed for findstr to work reliably with paths.
CHCP 437 >NUL
for /f "delims=" %%a in ('python -c "import sys; print(sys.executable)"') do set PYTHON_EXE_PATH=%%a
CHCP %ORIGINAL_CHCP% >NUL

echo Actual Python executable: %PYTHON_EXE_PATH%
echo %PYTHON_EXE_PATH% | findstr /I /C:"whisper_env" > nul
if errorlevel 1 (
    echo.
    echo CRITICAL ERROR: Virtual environment did not activate correctly.
    echo The Python executable being used (%PYTHON_EXE_PATH%) is NOT from the 'whisper_env'.
    echo This usually means 'call whisper_env\\Scripts\\activate.bat' failed silently or global Python is interfering.
    echo Common causes:
    echo   1. Issues with your main Python installation (e.g., Microsoft Store version, corrupted PATH).
    echo   2. Antivirus software interfering with script execution.
    echo   3. Errors within the 'activate.bat' script itself on this system.
    echo Please check your Python installation and PATH settings.
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)
echo ✓ Virtual environment Python is active.

echo.
echo Testing virtual environment (Old Test)...
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
echo If you see this message, the installation script completed ALL steps!
echo Review any WARNINGS or ERRORS above to identify issues.
echo.
echo To start WebTalk:
echo   .\\Launch.bat
echo.
echo DEBUG: Press any key to continue...
pause 