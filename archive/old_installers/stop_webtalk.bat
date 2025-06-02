@echo off
echo Stopping WebTalk server...

REM Check if virtual environment exists
if not exist "whisper_env\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run install.bat first to set up the environment.
    pause
    exit /b 1
)

REM Run the stop script
whisper_env\Scripts\python.exe stop_webtalk.py

pause 