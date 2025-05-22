# WebTalk - Voice Transcription Chrome Extension

WebTalk is a Chrome extension that provides real-time voice transcription using a local Whisper AI server. Simply right-click anywhere on a webpage, record your voice by holding down a button, and get instant transcription that you can copy to your clipboard.

## ✨ Features

- **Right-click to Record**: Start recording from any webpage with a simple right-click
- **Push-to-Talk**: Hold the record button to capture audio - release to stop
- **Real-time Transcription**: Powered by OpenAI Whisper 3 Turbo with CUDA acceleration
- **Local Processing**: All transcription happens on your computer - no data sent to external servers
- **Modern UI**: Beautiful, draggable recording window with smooth animations
- **Easy Copy**: Right-click the transcription to copy it to your clipboard
- **Cross-browser Compatible**: Works on any website

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** installed and added to PATH
- **NVIDIA GPU** with CUDA support (optional, but recommended for speed)
- **Google Chrome** browser

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd WebTalk
   ```

2. **Run the installation script**
   ```bash
   install.bat
   ```
   This will:
   - Create a Python virtual environment
   - Install PyTorch with CUDA support
   - Install Whisper and all dependencies
   - Test your CUDA setup

3. **Install the Chrome extension**
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the `chrome_extension` folder from this project

4. **Start the Whisper server**
   ```bash
   run.bat
   ```
   Keep this terminal window open while using the extension.

## 📖 How to Use

1. **Start the server**: Run `run.bat` to start the local Whisper API server
2. **Right-click anywhere** on a webpage to open the recording window
3. **Hold the record button** and speak clearly
4. **Release the button** when you're done speaking
5. **Wait for transcription** (usually takes a few seconds)
6. **Right-click the transcription** to copy it to your clipboard
7. The recording window will automatically close after copying

## 🛠️ Project Structure

```
WebTalk/
├── install.bat              # Installation script
├── run.bat                  # Server startup script
├── whisper_server.py        # FastAPI server for Whisper
├── chrome_extension/        # Chrome extension files
│   ├── manifest.json        # Extension manifest
│   ├── background.js        # Service worker
│   ├── content.js          # Content script
│   ├── content.css         # Recording window styles
│   ├── popup.html          # Extension popup
│   ├── popup.css           # Popup styles
│   ├── popup.js            # Popup functionality
│   └── icons/              # Extension icons
└── README.md               # This file
```

## ⚙️ Configuration

### Whisper Model

By default, the system uses Whisper "turbo" model. You can change this by editing `whisper_server.py`:

```python
# Line 82: Change the model name
transcriber = WhisperTranscriber("large-v3")  # or "medium", "small", etc.
```

### Server Port

The default port is 8000. To change it, edit `whisper_server.py`:

```python
# Bottom of file
uvicorn.run(app, host="127.0.0.1", port=8001)  # Change port here
```

And update the extension's `background.js` and `popup.js` to use the new port.

## 🔧 Troubleshooting

### Server Issues

**Problem**: "Server offline" in extension popup
- **Solution**: Make sure you've run `run.bat` and the server is running
- **Check**: Look for "Whisper server ready!" message in the terminal

**Problem**: CUDA not available
- **Solution**: Make sure you have an NVIDIA GPU and CUDA drivers installed
- **Fallback**: The system will automatically use CPU if CUDA isn't available

**Problem**: Model loading fails
- **Solution**: Check your internet connection - models are downloaded on first use
- **Alternative**: Try a smaller model like "base" or "small"

### Extension Issues

**Problem**: Context menu doesn't appear
- **Solution**: Make sure the extension is enabled in Chrome extensions page
- **Check**: Try refreshing the webpage

**Problem**: Microphone access denied
- **Solution**: Click the microphone icon in Chrome's address bar and allow access
- **Alternative**: Check Chrome settings → Privacy and security → Site Settings → Microphone

**Problem**: No transcription after recording
- **Solution**: Check that the Whisper server is running and accessible
- **Debug**: Open browser console (F12) and look for error messages

### Performance Tips

1. **Use a good microphone** - Built-in laptop mics may have poor quality
2. **Speak clearly** - Whisper works best with clear, well-paced speech
3. **Reduce background noise** - Find a quiet environment for best results
4. **CUDA acceleration** - Use an NVIDIA GPU for faster transcription
5. **Keep recordings short** - Transcription is faster for shorter audio clips

## 🔒 Privacy & Security

- **Local Processing**: All audio processing happens on your computer
- **No Data Transmission**: Your voice data never leaves your machine
- **No Storage**: Audio recordings are not saved to disk
- **Open Source**: You can inspect all the code to verify privacy claims

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space (for models)
- **Internet**: Required for initial model download

### Recommended Requirements
- **GPU**: NVIDIA GPU with 4GB+ VRAM
- **RAM**: 8GB or more
- **CPU**: Modern multi-core processor

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the amazing transcription model
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- Chrome Extensions team for the excellent platform

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Look at the browser console for error messages
3. Check the terminal where the server is running for error logs
4. Create an issue on the GitHub repository with detailed information

---

**Happy transcribing! 🎤✨** 