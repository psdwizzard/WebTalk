@echo off
echo ========================================
echo WebTalk with Settings App
echo ========================================
echo.

REM Change to the directory where this script is located
cd /d "%~dp0"

REM --- Add bundled ffmpeg to PATH ---
set FFMPEG_DIR=%~dp0ffmpeg_binaries
echo Adding bundled ffmpeg to PATH: %FFMPEG_DIR%
set PATH=%FFMPEG_DIR%;%PATH%
REM You can verify by uncommenting the next line
REM echo Current PATH: %PATH%
echo.
REM --- End ffmpeg PATH modification ---

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

call whisper_env\Scripts\activate.bat && python server.py --settings-app flask 