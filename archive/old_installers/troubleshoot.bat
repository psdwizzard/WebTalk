@echo off
echo ========================================
echo WebTalk - Troubleshooting Script
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ❌ Python not found in PATH
    echo Please install Python 3.8+ from https://python.org
    goto :end
) else (
    echo ✅ Python found
)

echo.
echo Checking virtual environment...
if exist "whisper_env\Scripts\python.exe" (
    echo ✅ Virtual environment exists
) else (
    echo ❌ Virtual environment not found
    echo Please run install_simple.bat first
    goto :end
)

echo.
echo Checking Python packages...
if exist "whisper_env\Scripts\activate.bat" (
    call whisper_env\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ❌ Virtual environment activation script not found
    echo Using system Python instead...
)

echo Checking PyTorch...
whisper_env\Scripts\python.exe -c "import torch; print(f'✅ PyTorch {torch.__version__} - CUDA: {torch.cuda.is_available()}')" 2>nul
if errorlevel 1 echo ❌ PyTorch not installed

echo Checking Whisper...
whisper_env\Scripts\python.exe -c "import whisper; print('✅ Whisper installed')" 2>nul
if errorlevel 1 echo ❌ Whisper not installed

echo Checking FastAPI...
whisper_env\Scripts\python.exe -c "import fastapi; print('✅ FastAPI installed')" 2>nul
if errorlevel 1 echo ❌ FastAPI not installed

echo.
echo Checking server status...
python -c "import requests; r = requests.get('http://localhost:9090/health', timeout=3); print(f'✅ Server running on port 9090 - Status: {r.status_code}')" 2>nul
if errorlevel 1 (
    echo ❌ Server not running on port 9090
    echo Try running: launch_webtalk.bat or run.bat
)

echo.
echo Checking configuration...
if exist "webtalk_config.json" (
    echo ✅ Configuration file exists
    type webtalk_config.json
) else (
    echo ⚠️  Configuration file not found (will be created on first run)
)

echo.
echo Checking Chrome extension files...
if exist "chrome_extension\manifest.json" (
    echo ✅ Chrome extension files found
    findstr "9090" chrome_extension\manifest.json >nul
    if errorlevel 1 (
        echo ❌ Extension still configured for old port
        echo Please reload the extension in Chrome
    ) else (
        echo ✅ Extension configured for port 9090
    )
) else (
    echo ❌ Chrome extension files not found
)

:end
echo.
echo ========================================
echo Troubleshooting complete!
echo ========================================
echo.
echo If you're still having issues:
echo 1. Try running install_simple.bat
echo 2. Check the logs in webtalk_launcher.log
echo 3. Make sure no antivirus is blocking the server
echo 4. Try temporarily disabling other Chrome extensions
echo.
pause 