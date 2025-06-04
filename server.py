#!/usr/bin/env python3
"""
WebTalk Whisper Server with Configuration Support
Speech-to-text transcription using OpenAI Whisper with desktop settings app.
"""

import os
import tempfile
import logging
import json
import threading
import subprocess
import sys
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional
import torch
import whisper
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration model
class ServerConfig(BaseModel):
    compute_engine: str = "gpu"
    model: str = "base"
    microphone: str = "default"
    server_port: int = 8000
    auth_key: str = ""
    openai_api_key: str = ""

# Global variables
model = None
current_config = ServerConfig()
config_file = "webtalk_config.json"

# Initialize the app
app = FastAPI(title="WebTalk Whisper API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_config():
    """Load configuration from file."""
    global current_config
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                current_config = ServerConfig(**config_data)
                logger.info(f"Configuration loaded: {current_config.model} model on {current_config.compute_engine}")
        else:
            # Create default config file
            save_config()
            logger.info("Created default configuration file")
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        current_config = ServerConfig()

def save_config():
    """Save current configuration to file."""
    try:
        with open(config_file, 'w') as f:
            json.dump(current_config.model_dump(), f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

def launch_settings_app(app_type="flask"):
    """Launch the settings desktop app."""
    try:
        # Choose which settings app to launch
        if app_type == "flask":
            app_file = "launch_settings.py"  # Use the launcher for better window handling
        else:
            app_file = "settings_app.py"
            
        # Launch settings app in a separate process
        if os.name == 'nt':  # Windows
            subprocess.Popen([sys.executable, app_file])
        else:  # Unix/Linux/Mac
            subprocess.Popen([sys.executable, app_file])
        logger.info(f"Settings app launcher started ({app_type})")
    except Exception as e:
        logger.error(f"Failed to launch settings app: {e}")

@app.on_event("startup")
async def startup_event():
    """Load configuration and Whisper model on startup."""
    global model
    
    # Load configuration first
    load_config()
    
    try:
        # Determine device based on config
        if current_config.compute_engine == "gpu" and torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
            
        logger.info(f"Loading Whisper model '{current_config.model}' on {device}...")
        model = whisper.load_model(current_config.model, device=device)
        logger.info("Whisper model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "WebTalk Whisper API is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return {
        "status": "healthy",
        "device": device,
        "model": current_config.model,
        "cuda_available": torch.cuda.is_available(),
        "cuda_devices": torch.cuda.device_count() if torch.cuda.is_available() else 0
    }

@app.get("/config")
async def get_config():
    """Get current server configuration."""
    return current_config.model_dump()

@app.post("/config")
async def update_config(config: ServerConfig):
    """Update server configuration."""
    global current_config, model
    
    try:
        old_config = current_config.model_dump()
        
        # Update configuration
        current_config = config
        save_config()
        
        # Check if we need to reload the model (model changed OR compute engine changed)
        needs_reload = (
            model is None or 
            config.model != old_config.get("model") or 
            config.compute_engine != old_config.get("compute_engine")
        )
        
        if needs_reload:
            device = "cuda" if config.compute_engine == "gpu" and torch.cuda.is_available() else "cpu"
            logger.info(f"Reloading model '{config.model}' on {device}...")
            model = whisper.load_model(config.model, device=device)
            logger.info("Model reloaded successfully!")
        
        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe uploaded audio file."""
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    logger.info(f"Processing audio file: {audio.filename}")
    
    try:
        # Read the uploaded file
        audio_content = await audio.read()
        
        if len(audio_content) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        # Transcribe
        result = model.transcribe(temp_file_path)
        
        # Clean up
        os.unlink(temp_file_path)
        
        logger.info(f"Transcription successful: {result['text'][:50]}...")
        
        return JSONResponse(content={
            "success": True,
            "transcription": result["text"],
            "language": result.get("language", "unknown"),
            "filename": audio.filename
        })
        
    except Exception as e:
        # Clean up on error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.get("/recorder", response_class=HTMLResponse)
async def get_recorder_interface():
    """Serve the web-based recording interface that replicates the Chrome extension functionality."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebTalk Recorder</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }

        .recorder-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            max-width: 500px;
            width: 90%;
            text-align: center;
        }

        .header {
            margin-bottom: 30px;
        }

        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }

        h1 {
            font-size: 2rem;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .subtitle {
            opacity: 0.8;
            font-size: 1rem;
        }

        .recording-area {
            margin: 30px 0;
        }

        .record-button {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            font-size: 2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
            margin-bottom: 20px;
        }

        .record-button:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 40px rgba(255, 107, 107, 0.6);
        }

        .record-button.recording {
            background: linear-gradient(45deg, #ff4757, #c44569);
            animation: pulse 2s infinite;
        }

        .record-button.processing {
            background: linear-gradient(45deg, #ffa502, #ff6348);
            cursor: not-allowed;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin: 20px 0;
        }

        .control-btn {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .control-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        .control-btn.primary {
            background: linear-gradient(45deg, #5f27cd, #341f97);
        }

        .control-btn.primary:hover {
            background: linear-gradient(45deg, #6c5ce7, #5f27cd);
        }

        .status {
            margin: 20px 0;
            font-size: 1rem;
            opacity: 0.9;
        }

        .transcription-area {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            min-height: 100px;
            text-align: left;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .transcription-placeholder {
            opacity: 0.6;
            font-style: italic;
            text-align: center;
        }

        .transcription-text {
            line-height: 1.6;
            font-size: 1rem;
        }

        .copy-button {
            background: linear-gradient(45deg, #00d2d3, #54a0ff);
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.3s ease;
            margin-top: 10px;
        }

        .copy-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 210, 211, 0.4);
        }

        .error {
            background: rgba(255, 107, 107, 0.2);
            border: 1px solid rgba(255, 107, 107, 0.5);
            color: #ff6b6b;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        }

        .success {
            background: rgba(46, 213, 115, 0.2);
            border: 1px solid rgba(46, 213, 115, 0.5);
            color: #2ed573;
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        }

        .hidden {
            display: none;
        }

        .server-status {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.1);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8rem;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #ff4757;
        }

        .status-indicator.connected {
            background: #2ed573;
        }
    </style>
</head>
<body>
    <div class="server-status">
        <div class="status-indicator" id="statusIndicator"></div>
        <span id="statusText">Checking server...</span>
    </div>

    <div class="recorder-container">
        <div class="header">
            <div class="logo">🎤</div>
            <h1>WebTalk Recorder</h1>
            <p class="subtitle">Voice Transcription Assistant</p>
        </div>

        <div class="recording-area">
            <button class="record-button" id="recordButton">
                <span id="recordIcon">🎙️</span>
            </button>
            
            <div class="controls hidden" id="recordingControls">
                <button class="control-btn" id="stopButton">⏹️ Stop</button>
                <button class="control-btn primary" id="stopCopyButton">📋 Stop & Copy</button>
            </div>
        </div>

        <div class="status" id="statusMessage">Click the microphone to start recording</div>

        <div class="transcription-area">
            <div class="transcription-placeholder" id="transcriptionPlaceholder">
                Your transcription will appear here...
            </div>
            <div class="transcription-text hidden" id="transcriptionText"></div>
            <button class="copy-button hidden" id="copyButton">📋 Copy to Clipboard</button>
        </div>

        <div id="errorMessage" class="error hidden"></div>
        <div id="successMessage" class="success hidden"></div>
    </div>

    <script>
        class WebTalkRecorder {
            constructor() {
                this.isRecording = false;
                this.mediaRecorder = null;
                this.audioChunks = [];
                this.stream = null;
                this.shouldAutoCopy = false;
                
                this.initializeElements();
                this.setupEventListeners();
                this.checkServerStatus();
            }

            initializeElements() {
                this.recordButton = document.getElementById('recordButton');
                this.recordIcon = document.getElementById('recordIcon');
                this.recordingControls = document.getElementById('recordingControls');
                this.stopButton = document.getElementById('stopButton');
                this.stopCopyButton = document.getElementById('stopCopyButton');
                this.statusMessage = document.getElementById('statusMessage');
                this.transcriptionPlaceholder = document.getElementById('transcriptionPlaceholder');
                this.transcriptionText = document.getElementById('transcriptionText');
                this.copyButton = document.getElementById('copyButton');
                this.errorMessage = document.getElementById('errorMessage');
                this.successMessage = document.getElementById('successMessage');
                this.statusIndicator = document.getElementById('statusIndicator');
                this.statusText = document.getElementById('statusText');
            }

            setupEventListeners() {
                this.recordButton.addEventListener('click', () => this.toggleRecording());
                this.stopButton.addEventListener('click', () => this.stopRecording());
                this.stopCopyButton.addEventListener('click', () => this.stopAndCopyRecording());
                this.copyButton.addEventListener('click', () => this.copyTranscription());
            }

            async checkServerStatus() {
                try {
                    const response = await fetch('/health');
                    if (response.ok) {
                        this.statusIndicator.classList.add('connected');
                        this.statusText.textContent = 'Server connected';
                        return true;
                    }
                } catch (error) {
                    console.error('Server check failed:', error);
                }
                
                this.statusIndicator.classList.remove('connected');
                this.statusText.textContent = 'Server disconnected';
                return false;
            }

            async toggleRecording() {
                if (this.isRecording) {
                    this.stopRecording();
                } else {
                    await this.startRecording();
                }
            }

            async startRecording() {
                try {
                    // Check server status first
                    const serverOk = await this.checkServerStatus();
                    if (!serverOk) {
                        this.showError('Server is not available. Please check if the WebTalk server is running.');
                        return;
                    }

                    // Request microphone access
                    this.stream = await navigator.mediaDevices.getUserMedia({ 
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true
                        } 
                    });

                    // Setup MediaRecorder
                    this.mediaRecorder = new MediaRecorder(this.stream, {
                        mimeType: 'audio/webm;codecs=opus'
                    });

                    this.audioChunks = [];
                    this.mediaRecorder.ondataavailable = (event) => {
                        if (event.data.size > 0) {
                            this.audioChunks.push(event.data);
                        }
                    };

                    this.mediaRecorder.onstop = () => {
                        this.processRecording();
                    };

                    // Start recording
                    this.mediaRecorder.start();
                    this.isRecording = true;
                    this.updateUI('recording');
                    
                } catch (error) {
                    console.error('Error starting recording:', error);
                    this.showError('Failed to start recording. Please check microphone permissions.');
                }
            }

            stopRecording() {
                if (this.mediaRecorder && this.isRecording) {
                    this.mediaRecorder.stop();
                    this.isRecording = false;
                    
                    // Stop all tracks
                    if (this.stream) {
                        this.stream.getTracks().forEach(track => track.stop());
                    }
                    
                    this.updateUI('processing');
                }
            }

            stopAndCopyRecording() {
                this.shouldAutoCopy = true;
                this.stopRecording();
            }

            async processRecording() {
                try {
                    // Create audio blob
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                    
                    if (audioBlob.size === 0) {
                        this.showError('No audio data recorded. Please try again.');
                        this.updateUI('idle');
                        return;
                    }

                    // Create form data
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'recording.webm');

                    // Send to server
                    const response = await fetch('/transcribe', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error(`Server error: ${response.status}`);
                    }

                    const result = await response.json();
                    
                    if (result.success && result.transcription) {
                        this.displayTranscription(result.transcription);
                        
                        if (this.shouldAutoCopy) {
                            await this.copyTranscription();
                            this.shouldAutoCopy = false;
                        }
                    } else {
                        this.showError('Transcription failed. Please try again.');
                    }

                } catch (error) {
                    console.error('Processing error:', error);
                    this.showError(`Failed to process recording: ${error.message}`);
                } finally {
                    this.updateUI('idle');
                }
            }

            displayTranscription(text) {
                this.transcriptionPlaceholder.classList.add('hidden');
                this.transcriptionText.classList.remove('hidden');
                this.copyButton.classList.remove('hidden');
                this.transcriptionText.textContent = text;
                this.statusMessage.textContent = 'Transcription complete!';
            }

            async copyTranscription() {
                try {
                    const text = this.transcriptionText.textContent;
                    await navigator.clipboard.writeText(text);
                    this.showSuccess('Transcription copied to clipboard!');
                } catch (error) {
                    console.error('Copy failed:', error);
                    this.showError('Failed to copy to clipboard. Please select and copy manually.');
                }
            }

            updateUI(state) {
                this.hideMessages();
                
                switch (state) {
                    case 'recording':
                        this.recordButton.classList.add('recording');
                        this.recordIcon.textContent = '⏸️';
                        this.recordingControls.classList.remove('hidden');
                        this.statusMessage.textContent = '🔴 Recording... Speak now!';
                        break;
                        
                    case 'processing':
                        this.recordButton.classList.remove('recording');
                        this.recordButton.classList.add('processing');
                        this.recordIcon.textContent = '⏳';
                        this.recordingControls.classList.add('hidden');
                        this.statusMessage.textContent = 'Processing transcription...';
                        break;
                        
                    case 'idle':
                    default:
                        this.recordButton.classList.remove('recording', 'processing');
                        this.recordIcon.textContent = '🎙️';
                        this.recordingControls.classList.add('hidden');
                        this.statusMessage.textContent = 'Click the microphone to start recording';
                        break;
                }
            }

            showError(message) {
                this.hideMessages();
                this.errorMessage.textContent = message;
                this.errorMessage.classList.remove('hidden');
            }

            showSuccess(message) {
                this.hideMessages();
                this.successMessage.textContent = message;
                this.successMessage.classList.remove('hidden');
                setTimeout(() => {
                    this.successMessage.classList.add('hidden');
                }, 3000);
            }

            hideMessages() {
                this.errorMessage.classList.add('hidden');
                this.successMessage.classList.add('hidden');
            }
        }

        // Initialize the recorder when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            new WebTalkRecorder();
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="WebTalk Whisper Server")
    parser.add_argument("--settings-app", choices=["flask", "tkinter", "none"], default="none",
                       help="Launch settings app (flask, tkinter, or none)")
    args = parser.parse_args()
    
    # Load config to get the port
    load_config()
    
    # Launch settings app if requested
    if args.settings_app != "none":
        launch_settings_app(args.settings_app)
    
    logger.info(f"Starting WebTalk Whisper Server on port {current_config.server_port}...")
    uvicorn.run(app, host="127.0.0.1", port=current_config.server_port, log_level="info") 