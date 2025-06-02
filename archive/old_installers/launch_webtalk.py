#!/usr/bin/env python3
"""
WebTalk Silent Launcher
Launches the WebTalk server without showing a terminal window.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path
import logging

# Configure logging to file
log_file = Path("webtalk_launcher.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also log to console for debugging
    ]
)
logger = logging.getLogger(__name__)

def check_virtual_env() -> bool:
    """Check if virtual environment exists."""
    venv_path = Path("whisper_env")
    if not venv_path.exists():
        logger.error("Virtual environment not found!")
        logger.error("Please run install.bat first to set up the environment.")
        return False
    
    # Check for Python executable
    python_exe = venv_path / "Scripts" / "python.exe"
    if not python_exe.exists():
        logger.error("Python executable not found in virtual environment!")
        return False
    
    return True

def get_python_executable() -> Path:
    """Get the path to the Python executable in the virtual environment."""
    return Path("whisper_env") / "Scripts" / "python.exe"

def is_server_running(port: int = 9090) -> bool:
    """Check if the server is already running."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except Exception:
        return False

def launch_server() -> subprocess.Popen:
    """Launch the WebTalk server in the background."""
    python_exe = get_python_executable()
    
    # Use CREATE_NO_WINDOW flag to hide the console window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    
    # Launch the server
    process = subprocess.Popen(
        [str(python_exe), "whisper_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    return process

def wait_for_server(port: int = 9090, timeout: int = 30) -> bool:
    """Wait for the server to start up."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_server_running(port):
            return True
        time.sleep(1)
    return False

def open_settings_page(port: int = 9090):
    """Open the settings page in the default browser."""
    url = f"http://127.0.0.1:{port}/settings"
    try:
        webbrowser.open(url)
        logger.info(f"Opened settings page: {url}")
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        logger.info(f"Please manually open: {url}")

def main():
    """Main launcher function."""
    logger.info("WebTalk Launcher starting...")
    
    # Check if virtual environment exists
    if not check_virtual_env():
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Load configuration to get port
    try:
        from config import ServerConfig
        config = ServerConfig()
        port = config.get("server_port", 9090)
    except Exception as e:
        logger.warning(f"Could not load config: {e}, using default port 9090")
        port = 9090
    
    # Check if server is already running
    if is_server_running(port):
        logger.info(f"Server is already running on port {port}")
        open_settings_page(port)
        return
    
    try:
        # Launch the server
        logger.info("Starting WebTalk server...")
        process = launch_server()
        
        # Wait for server to start
        logger.info("Waiting for server to start...")
        if wait_for_server(port, timeout=30):
            logger.info(f"Server started successfully on port {port}")
            
            # Open settings page
            time.sleep(2)  # Give server a moment to fully initialize
            open_settings_page(port)
            
            logger.info("WebTalk server is running in the background")
            logger.info(f"Settings page: http://127.0.0.1:{port}/settings")
            logger.info(f"API endpoint: http://127.0.0.1:{port}/transcribe")
            logger.info("Check webtalk_launcher.log for server logs")
            
        else:
            logger.error("Server failed to start within timeout period")
            process.terminate()
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 