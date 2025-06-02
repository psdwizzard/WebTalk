@echo off
echo ========================================
echo WebTalk - Environment Cleanup Script
echo ========================================
echo.
echo This script will stop all Python processes and clean up
echo the virtual environment to prepare for a fresh installation.
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - Good!
) else (
    echo WARNING: This script should be run as Administrator for best results.
    echo Right-click and select "Run as administrator"
    echo.
    pause
)

echo Stopping WebTalk server processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *whisper*" >nul 2>&1
taskkill /f /im pythonw.exe /fi "WINDOWTITLE eq *whisper*" >nul 2>&1

echo Stopping all Python processes that might be using the virtual environment...
echo (This might stop other Python programs temporarily)

REM Get list of Python processes and stop them
for /f "skip=1 tokens=2" %%i in ('wmic process where "name='python.exe'" get processid /format:csv') do (
    if not "%%i"=="" (
        echo Stopping Python process %%i
        taskkill /f /pid %%i >nul 2>&1
    )
)

for /f "skip=1 tokens=2" %%i in ('wmic process where "name='pythonw.exe'" get processid /format:csv') do (
    if not "%%i"=="" (
        echo Stopping Python process %%i
        taskkill /f /pid %%i >nul 2>&1
    )
)

echo Waiting for processes to fully terminate...
timeout /t 5 /nobreak >nul

echo Attempting to remove virtual environment...
if exist "whisper_env" (
    echo Removing whisper_env directory...
    
    REM Try normal removal
    rmdir /s /q "whisper_env" >nul 2>&1
    
    if exist "whisper_env" (
        echo Normal removal failed, trying with elevated permissions...
        
        REM Take ownership and grant full permissions
        takeown /f "whisper_env" /r /d y >nul 2>&1
        icacls "whisper_env" /grant administrators:F /t >nul 2>&1
        
        REM Try removal again
        rmdir /s /q "whisper_env" >nul 2>&1
        
        if exist "whisper_env" (
            echo Still having issues, renaming old environment...
            ren "whisper_env" "whisper_env_old_%RANDOM%"
            if exist "whisper_env" (
                echo ❌ Could not remove or rename virtual environment
                echo You may need to restart your computer and try again
            ) else (
                echo ✅ Old environment renamed successfully
            )
        ) else (
            echo ✅ Virtual environment removed successfully
        )
    ) else (
        echo ✅ Virtual environment removed successfully
    )
) else (
    echo ✅ No virtual environment found to remove
)

echo.
echo Cleanup complete!
echo.
echo Next steps:
echo 1. Run install_force.bat as Administrator
echo 2. If that fails, restart your computer and try again
echo.
pause 