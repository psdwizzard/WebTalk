#!/usr/bin/env python3
"""
WebTalk Settings App Launcher
This launcher sets the process icon before starting the main app.
"""

import sys
import ctypes
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
IMAGES_DIR = PROJECT_ROOT / "Images"

def set_process_icon():
    """Set the process icon before creating any windows"""
    try:
        # Set application user model ID
        shell32 = ctypes.windll.shell32
        shell32.SetCurrentProcessExplicitAppUserModelID("WebTalk.SettingsApp.1.0")
        
        # Get icon path
        icon_path = IMAGES_DIR / "WebTalk.ico"
        
        if icon_path.exists():
            # Load the icon
            user32 = ctypes.windll.user32
            hicon = user32.LoadImageW(
                None,
                str(icon_path),
                1,  # IMAGE_ICON
                0, 0,  # Use default size
                0x00000010  # LR_LOADFROMFILE
            )
            
            if hicon:
                # Set the icon for the current process
                kernel32 = ctypes.windll.kernel32
                process_handle = kernel32.GetCurrentProcess()
                
                # This is a more direct approach
                user32.SetClassLongPtrW(
                    user32.GetConsoleWindow(),
                    -34,  # GCL_HICON
                    hicon
                )
                
                print("Process icon set successfully!")
                return True
            else:
                print("Failed to load icon")
        else:
            print(f"Icon file not found: {icon_path}")
            
    except Exception as e:
        print(f"Error setting process icon: {e}")
    
    return False

if __name__ == "__main__":
    # Set the process icon first
    set_process_icon()
    
    # Now import and run the main app
    from settings_app_flask import WebTalkSettingsApp
    
    app = WebTalkSettingsApp()
    app.run() 
