@echo off
echo Starting WebTalk Whisper API Server...

REM Check if virtual environment exists
if not exist "whisper_env\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run install.bat first to set up the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call whisper_env\Scripts\activate.bat

REM Start the API server
echo Starting Whisper API server on http://localhost:8000
echo Press Ctrl+C to stop the server.
echo.
python whisper_server.py 