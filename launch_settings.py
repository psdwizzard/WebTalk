#!/usr/bin/env python3
"""
Settings App Launcher - Ensures proper window visibility
"""

import subprocess
import sys
import time
import os

def main():
    """Launch the settings app with proper timing"""
    print("Launching WebTalk Settings App...")
    
    # Give the main server a moment to fully start
    time.sleep(3)
    
    # Launch the Flask settings app
    try:
        # Use the same Python executable as the current process
        settings_script = os.path.join(os.path.dirname(__file__), "settings_app_flask.py")
        
        # Launch with proper window handling
        if os.name == 'nt':  # Windows
            # Use Popen to avoid creating a new console window
            subprocess.Popen([sys.executable, settings_script], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
        else:  # Unix/Linux/Mac
            subprocess.Popen([sys.executable, settings_script])
            
    except Exception as e:
        print(f"Error launching settings app: {e}")
        print("You can manually run: python settings_app_flask.py")

if __name__ == "__main__":
    main() 