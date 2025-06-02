# WebTalk Archive

This folder contains old, duplicate, and development files that have been moved out of the main project directory for better organization.

## Folder Structure

### `old_installers/`
- `install.bat` - Original installer script (replaced by `install_simple.bat`)

### `old_chrome_extension_files/`
- `background_debug.js` - Debug version of background script
- `content_debug.js` - Early debug version of content script
- `content_debug2.js` - Second debug version of content script
- `content_simple.js` - Simplified content script version
- `content_clean.js` - Cleaned up content script version
- `content_fixed.js` - Fixed content script version

### `build_files/`
- `fix_whisper_assets.ps1` - PowerShell script for fixing Whisper assets
- `create_placeholder_icons.py` - Script for creating placeholder icons
- `__pycache__/` - Python cache files

**Note**: The `executable_install/` directory remains in the root for optional executable building.

### `logs/`
- `webtalk_launcher.log` - Old launcher log files

## Current Active Files

The main project now uses these clean, active files:

**Root Directory:**
- `install_simple.bat` - Main installer
- `launch_webtalk.bat` - Silent launcher
- `run.bat` - Traditional launcher with terminal
- `troubleshoot.bat` - Diagnostic script
- `whisper_server.py` - Main server
- `config.py` - Configuration management
- `settings.html` - Web settings interface

**Chrome Extension:**
- `background.js` - Main background script
- `content.js` - Main content script
- `manifest.json` - Extension manifest
- `popup.html/js/css` - Extension popup
- `content.css` - Content script styles

## Notes

- Files in this archive are kept for reference but are not actively used
- The main project structure is now much cleaner and easier to navigate
- If you need to reference old implementations, they can be found here 