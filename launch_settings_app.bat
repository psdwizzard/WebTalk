@echo off
echo Starting WebTalk Settings App...
cd /d "%~dp0"
whisper_env\Scripts\python.exe webtalk_settings.py
pause 