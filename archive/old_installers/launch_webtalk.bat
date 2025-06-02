@echo off
REM WebTalk Silent Launcher
REM Launches the WebTalk server without showing a terminal window

REM Check if virtual environment exists
if not exist "whisper_env\Scripts\pythonw.exe" (
    echo Error: Virtual environment not found!
    echo Please run install.bat first to set up the environment.
    pause
    exit /b 1
)

REM Launch the server using pythonw.exe (windowless Python)
echo Starting WebTalk server in background...
start "" "whisper_env\Scripts\pythonw.exe" launch_webtalk.py

REM Exit immediately (don't wait)
exit /b 0 