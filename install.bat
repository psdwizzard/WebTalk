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
    echo Press any key to exit...
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

echo Running: python -m venv whisper_env
python -m venv whisper_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Error code: %errorlevel%
    echo Make sure you have the full Python installation (not Microsoft Store version)
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo ✓ Virtual environment created successfully

echo Activating virtual environment...
echo Running: call whisper_env\Scripts\activate.bat
call whisper_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Error code: %errorlevel%
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo ✓ Virtual environment activated successfully

REM Test that we're in the virtual environment
echo Testing virtual environment...
python -c "import sys; print('Python executable:', sys.executable)"
if errorlevel 1 (
    echo ERROR: Virtual environment test failed
    echo Press any key to exit...
    pause
    exit /b 1
)

echo ✓ Virtual environment test passed

echo Installing PyTorch with CUDA support...
echo Running: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
if errorlevel 1 (
    echo WARNING: CUDA PyTorch installation failed (Error code: %errorlevel%)
    echo Trying CPU version...
    echo Running: pip install torch torchaudio
    pip install torch torchaudio
    if errorlevel 1 (
        echo ERROR: Failed to install PyTorch (Error code: %errorlevel%)
        echo This is a critical dependency - installation cannot continue
        echo.
        echo Try these solutions:
        echo 1. Check your internet connection
        echo 2. Try running as administrator
        echo 3. Update pip: python -m pip install --upgrade pip
        echo.
        echo Press any key to exit...
        pause
        exit /b 1
    )
    echo ✓ PyTorch CPU version installed successfully
) else (
    echo ✓ PyTorch CUDA version installed successfully
)

echo Installing OpenAI Whisper...
echo Running: pip install openai-whisper
pip install openai-whisper
if errorlevel 1 (
    echo ERROR: Failed to install OpenAI Whisper (Error code: %errorlevel%)
    echo.
    echo Try these solutions:
    echo 1. Check your internet connection
    echo 2. Try running as administrator  
    echo 3. Update pip: python -m pip install --upgrade pip
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo ✓ OpenAI Whisper installed successfully

echo Installing web framework dependencies...
echo Running: pip install fastapi uvicorn python-multipart requests pydantic
pip install fastapi uvicorn python-multipart requests pydantic
if errorlevel 1 (
    echo ERROR: Failed to install web dependencies (Error code: %errorlevel%)
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo ✓ Web framework dependencies installed successfully

echo Installing Flask for settings app...
echo Running: pip install flask
pip install flask
if errorlevel 1 (
    echo ERROR: Failed to install Flask (Error code: %errorlevel%)
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo ✓ Flask installed successfully

echo Installing PyWebView for GUI...
echo Running: pip install pywebview[win32]
pip install pywebview[win32]
if errorlevel 1 (
    echo WARNING: Failed to install PyWebView with win32 dependencies (Error code: %errorlevel%)
    echo Trying basic installation...
    echo Running: pip install pywebview
    pip install pywebview
    if errorlevel 1 (
        echo WARNING: Failed to install PyWebView (Error code: %errorlevel%)
        echo The Settings GUI may not work properly
        echo You can still use the Chrome extension with the server
        echo.
    ) else (
        echo ✓ PyWebView basic version installed successfully
    )
) else (
    echo ✓ PyWebView with Windows dependencies installed successfully
)

echo Installing additional dependencies...
echo Running: pip install psutil numpy sounddevice
pip install psutil numpy sounddevice
if errorlevel 1 (
    echo WARNING: Some optional dependencies failed to install (Error code: %errorlevel%)
    echo WebTalk should still work but some features may be limited
    echo.
)

echo Updating pip to latest version...
echo Running: python -m pip install --upgrade pip
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
echo Installation completed successfully! Press any key to continue...
pause 