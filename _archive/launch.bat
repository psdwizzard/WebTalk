@echo off
echo ========================================
echo WebTalk with Settings App
echo ========================================
echo.

REM Change to the directory where this script is located
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "whisper_env\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

echo Starting WebTalk server with settings app...
echo The settings app will open automatically.
echo Press Ctrl+C to stop the server
echo.

call whisper_env\Scripts\activate.bat && python Python\server.py --settings-app flask 
