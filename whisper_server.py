#!/usr/bin/env python3
"""
WebTalk Whisper API Server
Local speech-to-text transcription using OpenAI Whisper with CUDA support.
"""

import os
import io
import tempfile
import logging
from typing import Optional
from pathlib import Path

import torch
import whisper
import soundfile as sf
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhisperTranscriber:
    """Whisper transcription service with CUDA support."""
    
    def __init__(self, model_name: str = "turbo"):
        """
        Initialize the Whisper transcriber.
        
        Args:
            model_name: Whisper model to use (turbo, large-v3, etc.)
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def transcribe(self, audio_file_path: str) -> dict:
        """
        Transcribe audio file.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Dictionary containing transcription results
        """
        try:
            logger.info(f"Transcribing: {audio_file_path}")
            result = self.model.transcribe(audio_file_path)
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", [])
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

# Initialize the app and transcriber
app = FastAPI(
    title="WebTalk Whisper API",
    description="Local Whisper transcription service for WebTalk Chrome extension",
    version="1.0.0"
)

# Add CORS middleware to allow Chrome extension to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your extension
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global transcriber instance
transcriber: Optional[WhisperTranscriber] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the transcriber on startup."""
    global transcriber
    try:
        transcriber = WhisperTranscriber()
        logger.info("Whisper server ready!")
    except Exception as e:
        logger.error(f"Failed to initialize transcriber: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "WebTalk Whisper API Server",
        "status": "running",
        "device": transcriber.device if transcriber else "unknown",
        "model": transcriber.model_name if transcriber else "unknown"
    }

@app.get("/health")
async def health_check():
    """Detailed health check."""
    if not transcriber:
        raise HTTPException(status_code=503, detail="Transcriber not initialized")
    
    return {
        "status": "healthy",
        "device": transcriber.device,
        "model": transcriber.model_name,
        "cuda_available": torch.cuda.is_available(),
        "cuda_devices": torch.cuda.device_count() if torch.cuda.is_available() else 0
    }

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe uploaded audio file.
    
    Args:
        audio: Audio file upload
        
    Returns:
        JSON response with transcription
    """
    if not transcriber:
        raise HTTPException(status_code=503, detail="Transcriber not initialized")
    
    # Accept audio files and WebM from Chrome MediaRecorder
    valid_types = ["audio/", "video/webm", "application/octet-stream"]
    if not audio.content_type or not any(audio.content_type.startswith(t) for t in valid_types):
        logger.warning(f"Rejected file type: {audio.content_type}")
        raise HTTPException(status_code=400, detail=f"Invalid audio file type: {audio.content_type}")
    
    logger.info(f"Processing audio file: {audio.filename}, type: {audio.content_type}")
    
    try:
        # Read the uploaded file
        audio_content = await audio.read()
        logger.info(f"Audio content size: {len(audio_content)} bytes")
        
        if len(audio_content) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Check minimum file size (WebM header alone is ~100+ bytes)
        if len(audio_content) < 100:
            raise HTTPException(status_code=400, detail=f"Audio file too small ({len(audio_content)} bytes). Please record for at least 1-2 seconds.")
        
        # Log first few bytes to debug format
        logger.info(f"Audio file header: {audio_content[:20].hex()}")
        
        # Create temporary file for the audio
        file_suffix = ".webm" if audio.content_type.startswith("video/webm") or audio.content_type.startswith("audio/webm") else ".wav"
        with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as temp_file:
            
            if audio.content_type == "audio/wav":
                # Write WAV directly
                temp_file.write(audio_content)
                temp_file_path = temp_file.name
                logger.info(f"Saved as WAV: {temp_file_path}")
            elif audio.content_type.startswith("video/webm") or audio.content_type.startswith("audio/webm"):
                # Write WebM directly and let Whisper handle it
                temp_file.write(audio_content)
                temp_file_path = temp_file.name
                logger.info(f"Saved as WebM: {temp_file_path}")
            else:
                # Try to convert using soundfile
                try:
                    logger.info("Attempting soundfile conversion...")
                    audio_data, sample_rate = sf.read(io.BytesIO(audio_content))
                    # Save as WAV
                    temp_file_path = temp_file.name.replace(file_suffix, ".wav")
                    sf.write(temp_file_path, audio_data, sample_rate)
                    logger.info(f"Converted to WAV: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Soundfile conversion failed: {e}, trying direct write")
                    temp_file.write(audio_content)
                    temp_file_path = temp_file.name
                    logger.info(f"Saved as-is: {temp_file_path}")
        
        logger.info(f"Temporary file created: {temp_file_path}, size: {os.path.getsize(temp_file_path)} bytes")
        
        # Verify the file was written correctly
        if os.path.getsize(temp_file_path) != len(audio_content):
            logger.warning(f"File size mismatch: expected {len(audio_content)}, got {os.path.getsize(temp_file_path)}")
        
        # Transcribe the audio
        result = transcriber.transcribe(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        logger.info(f"Transcription successful: {result['text'][:100]}...")
        
        return JSONResponse(content={
            "success": True,
            "transcription": result["text"],
            "language": result["language"],
            "filename": audio.filename
        })
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting WebTalk Whisper API Server...")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    ) 