#!/usr/bin/env python3
"""
WebTalk Server Manager
Stop the WebTalk server running in the background.
"""

import psutil
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_webtalk_processes():
    """Find all WebTalk server processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('whisper_server.py' in arg for arg in cmdline):
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def stop_server():
    """Stop all WebTalk server processes."""
    processes = find_webtalk_processes()
    
    if not processes:
        logger.info("No WebTalk server processes found.")
        return
    
    logger.info(f"Found {len(processes)} WebTalk server process(es)")
    
    for proc in processes:
        try:
            logger.info(f"Stopping process {proc.pid}: {proc.name()}")
            proc.terminate()
            
            # Wait for process to terminate
            proc.wait(timeout=10)
            logger.info(f"Process {proc.pid} stopped successfully")
            
        except psutil.TimeoutExpired:
            logger.warning(f"Process {proc.pid} did not terminate gracefully, forcing...")
            try:
                proc.kill()
                logger.info(f"Process {proc.pid} killed")
            except psutil.NoSuchProcess:
                logger.info(f"Process {proc.pid} already terminated")
        except psutil.NoSuchProcess:
            logger.info(f"Process {proc.pid} already terminated")
        except Exception as e:
            logger.error(f"Error stopping process {proc.pid}: {e}")

def check_server_status():
    """Check if the server is running."""
    processes = find_webtalk_processes()
    if processes:
        logger.info(f"WebTalk server is running ({len(processes)} process(es))")
        for proc in processes:
            logger.info(f"  PID: {proc.pid}, Name: {proc.name()}")
        return True
    else:
        logger.info("WebTalk server is not running")
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        check_server_status()
    else:
        logger.info("WebTalk Server Manager")
        logger.info("Stopping WebTalk server...")
        stop_server()
        logger.info("Done.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1) 