@echo off
echo Starting WebTalk - Whisper Server & Settings App...
cd /d "%~dp0"

echo Starting Whisper Server...
start "WebTalk Whisper Server" whisper_env\Scripts\python.exe server.py

echo Waiting for server to initialize...
timeout /t 3 /nobreak >nul

echo Starting Settings App...
whisper_env\Scripts\python.exe settings_app_flask.py

pause 