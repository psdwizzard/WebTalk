@echo off
echo Starting WebTalk - Unified Server & Settings...
cd /d "%~dp0"
whisper_env\Scripts\python.exe settings_app_flask.py
pause 