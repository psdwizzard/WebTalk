# WebTalk - Voice Transcription Chrome Extension

A simple Chrome extension that lets you record and transcribe speech using OpenAI Whisper AI.

## Quick Setup

### 1. Install Dependencies
```bash
# Run the installer (this will take a few minutes)
install.bat
```

### 2. Start the Server

**Option A: With Settings App (Recommended)**
```bash
# Start server with desktop settings app
run_with_settings.bat
```

**Option B: Basic Server Only**
```bash
# Start the Whisper server only
run.bat
```

The server will start on `http://localhost:8000` (or your configured port)

### 3. Install Chrome Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the `chrome_extension` folder

## How to Use

1. **Start the server** by running `run_with_settings.bat` (recommended)
2. **Configure settings** in the desktop app that opens automatically
3. **Right-click anywhere** on a webpage
4. **Select "🎤 Start WebTalk Recording"**
5. **Hold the record button** and speak
6. **Release to transcribe** - text appears in the window
7. **Right-click the transcription** to copy to clipboard

## Settings App Features

The desktop settings app allows you to configure:

- **Compute Engine**: Choose GPU (CUDA) or CPU processing
- **Model Selection**: Pick from Tiny, Base, Small, Medium, Large, Large-v2, Large-v3, or Turbo
- **Microphone**: Select your preferred audio input device
- **Server Port**: Change the port the server runs on
- **Authentication**: Optional security key for API access
- **OpenAI Fallback**: API key for when local hardware is insufficient

Settings are automatically saved and applied to the running server!

## Requirements

- Python 3.8 or higher
- Chrome browser
- Microphone access
- ~2GB disk space for models

## Troubleshooting

### Server won't start
- Make sure you ran `install.bat` first
- Check that Python is installed: `python --version`
- Try running `install.bat` again

### Extension not working
- Make sure the server is running (`run.bat`)
- Check that the extension is enabled in Chrome
- Allow microphone access when prompted

### No transcription
- Speak for at least 1-2 seconds
- Make sure your microphone is working
- Check the browser console for errors (F12)

## What Gets Installed

- Virtual environment in `whisper_env/`
- PyTorch (for AI processing)
- OpenAI Whisper (speech recognition)
- FastAPI (web server)

## Files

- `install.bat` - Sets up the environment
- `run_with_settings.bat` - Starts server with settings app (recommended)
- `run.bat` - Starts the server only
- `server.py` - The Whisper API server with configuration support
- `settings_app.py` - Beautiful desktop settings interface
- `chrome_extension/` - The Chrome extension files
- `webtalk_config.json` - Configuration file (auto-generated)

That's it! Now with a beautiful settings interface that matches your Chrome extension! 