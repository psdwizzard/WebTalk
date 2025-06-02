@echo off
echo ========================================
echo WebTalk - Installation Script
echo ========================================
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
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✓ Python found

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Check if we're on Windows and install Windows-specific dependencies
echo Checking Windows dependencies...

REM Check for Visual C++ Redistributable
echo Checking Visual C++ Redistributable...
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Visual C++ Redistributable may not be installed
    echo PyWebView and other components may require it
    echo Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
)

REM Check for WebView2 Runtime
echo Checking WebView2 Runtime...
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if errorlevel 1 (
    reg query "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
    if errorlevel 1 (
        echo WARNING: WebView2 Runtime may not be installed
        echo WebTalk Settings GUI requires WebView2 Runtime
        echo Download from: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
        echo.
    )
)

echo Creating virtual environment...
if exist whisper_env (
    echo Virtual environment already exists, removing old one...
    rmdir /s /q whisper_env
)

python -m venv whisper_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure you have the full Python installation (not Microsoft Store version)
    pause
    exit /b 1
)

echo ✓ Virtual environment created

echo Activating virtual environment...
call whisper_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing PyTorch with CUDA support...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
if errorlevel 1 (
    echo WARNING: CUDA PyTorch installation failed, trying CPU version...
    pip install torch torchaudio
    if errorlevel 1 (
        echo ERROR: Failed to install PyTorch
        pause
        exit /b 1
    )
)

echo Installing OpenAI Whisper...
pip install openai-whisper
if errorlevel 1 (
    echo ERROR: Failed to install OpenAI Whisper
    pause
    exit /b 1
)

echo Installing web framework dependencies...
pip install fastapi uvicorn python-multipart requests pydantic
if errorlevel 1 (
    echo ERROR: Failed to install web dependencies
    pause
    exit /b 1
)

echo Installing Flask for settings app...
pip install flask
if errorlevel 1 (
    echo ERROR: Failed to install Flask
    pause
    exit /b 1
)

echo Installing PyWebView for GUI...
REM Install PyWebView with Windows-specific dependencies
pip install pywebview[win32]
if errorlevel 1 (
    echo WARNING: Failed to install PyWebView with win32 dependencies, trying basic installation...
    pip install pywebview
    if errorlevel 1 (
        echo ERROR: Failed to install PyWebView
        echo The Settings GUI may not work properly
        echo You can still use the Chrome extension with the server
        echo.
    )
)

echo Installing additional dependencies...
pip install psutil threading sounddevice numpy
if errorlevel 1 (
    echo WARNING: Some optional dependencies failed to install
    echo WebTalk should still work but some features may be limited
    echo.
)

echo Updating pip to latest version...
python -m pip install --upgrade pip

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo WebTalk has been installed successfully!
echo.
echo To start WebTalk:
echo   .\Launch.bat
echo.
echo If you encounter issues:
echo 1. Make sure you have Visual C++ Redistributable installed
echo 2. Make sure you have WebView2 Runtime installed  
echo 3. Try running as administrator
echo 4. Check that Windows Defender isn't blocking the application
echo.
echo For Chrome Extension:
echo 1. Open Chrome and go to chrome://extensions/
echo 2. Enable Developer mode
echo 3. Click "Load unpacked" and select the chrome_extension folder
echo.
pause 