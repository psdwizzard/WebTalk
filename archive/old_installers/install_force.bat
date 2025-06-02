@echo off
echo ========================================
echo WebTalk - Force Installation Script
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - Good!
) else (
    echo This script should be run as Administrator for best results.
    echo Right-click and select "Run as administrator"
    echo.
    echo Continuing anyway...
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Stopping any running WebTalk processes...

REM Stop any running WebTalk servers
taskkill /f /im python.exe /fi "WINDOWTITLE eq WebTalk*" >nul 2>&1
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq WebTalk*" >nul 2>&1

REM Stop processes that might be using the virtual environment
echo Stopping Python processes that might be using the virtual environment...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| find "python.exe"') do (
    echo Stopping process %%i
    taskkill /f /pid %%i >nul 2>&1
)
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq pythonw.exe" /fo csv ^| find "pythonw.exe"') do (
    echo Stopping process %%i
    taskkill /f /pid %%i >nul 2>&1
)

echo Waiting for processes to fully terminate...
timeout /t 3 /nobreak >nul

REM Try to remove existing environment with force
if exist "whisper_env" (
    echo Attempting to remove existing virtual environment...
    
    REM Try normal removal first
    rmdir /s /q "whisper_env" >nul 2>&1
    
    REM If that fails, try with takeown and icacls (requires admin)
    if exist "whisper_env" (
        echo Normal removal failed, trying with elevated permissions...
        takeown /f "whisper_env" /r /d y >nul 2>&1
        icacls "whisper_env" /grant administrators:F /t >nul 2>&1
        rmdir /s /q "whisper_env" >nul 2>&1
    )
    
    REM If still exists, rename it and create new one
    if exist "whisper_env" (
        echo Renaming old environment and creating new one...
        ren "whisper_env" "whisper_env_old_%RANDOM%" >nul 2>&1
    )
)

REM Create virtual environment
echo Creating new virtual environment...
python -m venv whisper_env
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    echo Try running this script as Administrator
    pause
    exit /b 1
)

echo Activating virtual environment...
call whisper_env\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip --quiet

echo Installing core dependencies with specific versions...
pip install --quiet numpy==1.24.4
if errorlevel 1 (
    echo Warning: numpy installation had issues, continuing...
)

pip install --quiet pandas==2.0.3
if errorlevel 1 (
    echo Warning: pandas installation had issues, continuing...
)

echo Installing PyTorch with CUDA support...
pip install --quiet torch torchaudio torchvision --index-url https://download.pytorch.org/whl/cu118
if errorlevel 1 (
    echo Warning: PyTorch installation had issues, trying CPU version...
    pip install --quiet torch torchaudio torchvision
)

echo Installing Whisper and other dependencies...
pip install --quiet openai-whisper
pip install --quiet fastapi "uvicorn[standard]"
pip install --quiet python-multipart aiofiles
pip install --quiet "pydantic>=2.0.0"
pip install --quiet soundfile librosa
pip install --quiet psutil requests

echo.
echo Testing installation...
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')" 2>nul
if errorlevel 1 (
    echo Warning: PyTorch test failed
)

python -c "import whisper; print('Whisper imported successfully')" 2>nul
if errorlevel 1 (
    echo Warning: Whisper test failed
)

python -c "import fastapi; print('FastAPI imported successfully')" 2>nul
if errorlevel 1 (
    echo Warning: FastAPI test failed
)

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
echo If you see any warnings above, run troubleshoot.bat to check the installation.
echo.
pause 