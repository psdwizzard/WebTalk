// WebTalk Content Script - Fixed Version
// Handles the recording interface and audio capture

class WebTalkRecorder {
  constructor() {
    this.isRecording = false;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.recordingWindow = null;
    this.stream = null;
    this.outsideClickHandler = null;
    this.keyHandler = null;
    this.recordingStartTime = null;
    this.shouldAutoCopy = false;
  }

  // Show the recording window
  async showRecordingWindow(x = 100, y = 100) {
    if (this.recordingWindow) {
      this.closeRecordingWindow();
    }

    // Check if server is running first
    try {
      const serverStatus = await this.checkServerStatus();
      if (!serverStatus || !serverStatus.success) {
        this.showErrorDialog(serverStatus ? serverStatus.error : 'Unable to check server status');
        return;
      }
    } catch (error) {
      this.showErrorDialog(`Server check failed: ${error.message}`);
      return;
    }

    this.createRecordingWindow(x, y);
    await this.setupAudio();
    
    // Auto-start recording immediately
    if (this.recordingWindow && this.stream) {
        this.startRecording();
    }
  }

  // Create the recording window UI
  createRecordingWindow(x, y) {
    this.recordingWindow = document.createElement('div');
    this.recordingWindow.id = 'webTalkWindow';
    this.recordingWindow.innerHTML = `
      <div class="webtalk-header">
        <span class="webtalk-title">🎤 WebTalk</span>
        <button class="webtalk-close" title="Close">×</button>
      </div>
      <div class="webtalk-content">
        <div class="webtalk-controls">
          <button class="webtalk-record-btn" title="Recording in progress">
            <span class="record-icon">🎙️</span>
            <span class="record-text">Recording...</span>
          </button>
        </div>
        <div class="webtalk-transcription">
          <div class="transcription-placeholder">
            Preparing to record... Speak when recording starts.
          </div>
        </div>
        <div class="webtalk-status">🔴 Recording in progress...</div>
      </div>
    `;

    // Position the window
    this.recordingWindow.style.left = `${Math.min(x, window.innerWidth - 350)}px`;
    this.recordingWindow.style.top = `${Math.min(y, window.innerHeight - 250)}px`;

    document.body.appendChild(this.recordingWindow);

    // Add event listeners
    this.setupEventListeners();

    // Make window draggable
    this.makeDraggable();
  }

  // Setup event listeners for the recording window
  setupEventListeners() {
    const closeBtn = this.recordingWindow.querySelector('.webtalk-close');
    const transcriptionArea = this.recordingWindow.querySelector('.webtalk-transcription');

    // Initially, we'll set up for recording state since we auto-start
    this.setupRecordingStateListeners();

    // Close button
    closeBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.closeRecordingWindow();
    });

    // Right-click on transcription to copy
    transcriptionArea.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.copyTranscription();
    });

    // ESC key to close
    this.keyHandler = (e) => {
      if (e.key === 'Escape' && this.recordingWindow) {
        this.closeRecordingWindow();
      }
    };
    document.addEventListener('keydown', this.keyHandler);

    // Less aggressive click outside handler
    this.outsideClickHandler = (e) => {
      // Only close if clicking on very specific elements to avoid blocking other extensions
      if (this.recordingWindow && 
          !this.recordingWindow.contains(e.target) && 
          (e.target === document.body || e.target === document.documentElement)) {
        setTimeout(() => {
          if (this.recordingWindow) {
            this.closeRecordingWindow();
          }
        }, 100);
      }
    };
    // Use capture phase to get events first, but be less aggressive
    document.addEventListener('click', this.outsideClickHandler, { capture: false, passive: true });
  }

  // Setup listeners for recording state (show stop buttons)
  setupRecordingStateListeners() {
    // Replace the controls with stop buttons
    const controlsDiv = this.recordingWindow.querySelector('.webtalk-controls');
    controlsDiv.className = 'webtalk-controls recording';
    controlsDiv.innerHTML = `
      <button class="webtalk-stop-btn" id="stopBtn">
        <span>⏹️</span>
        <span>Stop</span>
      </button>
      <button class="webtalk-stop-btn primary" id="stopCopyBtn">
        <span>📋</span>
        <span>Stop & Copy</span>
      </button>
    `;

    // Add event listeners for stop buttons
    const stopBtn = this.recordingWindow.querySelector('#stopBtn');
    const stopCopyBtn = this.recordingWindow.querySelector('#stopCopyBtn');

    stopBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.stopRecording();
    });

    stopCopyBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.stopAndCopyRecording();
    });
  }

  // Stop recording and copy result to clipboard
  async stopAndCopyRecording() {
    this.shouldAutoCopy = true;
    this.stopRecording();
  }

  // Make the window draggable
  makeDraggable() {
    const header = this.recordingWindow.querySelector('.webtalk-header');
    let isDragging = false;
    let offset = { x: 0, y: 0 };

    header.addEventListener('mousedown', (e) => {
      if (e.target.classList.contains('webtalk-close')) return;
      isDragging = true;
      offset.x = e.clientX - this.recordingWindow.offsetLeft;
      offset.y = e.clientY - this.recordingWindow.offsetTop;
      header.style.cursor = 'grabbing';
      e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
      if (isDragging) {
        this.recordingWindow.style.left = `${e.clientX - offset.x}px`;
        this.recordingWindow.style.top = `${e.clientY - offset.y}px`;
      }
    });

    document.addEventListener('mouseup', () => {
      isDragging = false;
      header.style.cursor = 'grab';
    });
  }

  // Setup audio recording
  async setupAudio() {
    try {
      console.log('WebTalk: Requesting microphone access...');
      
      // Check if microphone is available
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioDevices = devices.filter(device => device.kind === 'audioinput');
      console.log('WebTalk: Found audio devices:', audioDevices.length);
      
      if (audioDevices.length === 0) {
        throw new Error('No microphone found on this device');
      }

      this.stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        } 
      });
      
      console.log('WebTalk: Audio stream obtained:', this.stream);
      console.log('WebTalk: Audio tracks:', this.stream.getAudioTracks());
      
      // Test if tracks are active
      const audioTracks = this.stream.getAudioTracks();
      if (audioTracks.length > 0) {
        console.log('WebTalk: Audio track state:', audioTracks[0].readyState);
        console.log('WebTalk: Audio track enabled:', audioTracks[0].enabled);
        console.log('WebTalk: Audio track settings:', audioTracks[0].getSettings());
      }
      
      console.log('WebTalk: Audio setup complete');
      this.updateStatus('Microphone access granted - Starting recording...');
      
    } catch (error) {
      console.error('WebTalk: Audio setup failed:', error);
      if (error.name === 'NotAllowedError') {
        this.showError('Microphone access denied. Please allow microphone access in your browser settings.');
      } else if (error.name === 'NotFoundError') {
        this.showError('No microphone found. Please check your audio devices.');
      } else {
        this.showError(`Audio setup failed: ${error.message}`);
      }
    }
  }

  // Start recording
  startRecording() {
    if (this.isRecording || !this.stream) {
      console.log('WebTalk: Cannot start recording - already recording or no stream');
      console.log('WebTalk: isRecording:', this.isRecording, 'hasStream:', !!this.stream);
      return;
    }

    try {
      console.log('WebTalk: Starting recording...');
      console.log('WebTalk: Stream active:', this.stream.active);
      console.log('WebTalk: Audio tracks active:', this.stream.getAudioTracks().map(t => ({
        id: t.id,
        enabled: t.enabled,
        readyState: t.readyState,
        muted: t.muted
      })));

      this.audioChunks = [];
      this.recordingStartTime = Date.now();
      
      // Test MediaRecorder support
      console.log('WebTalk: MediaRecorder.isTypeSupported("audio/webm;codecs=opus"):', 
                  MediaRecorder.isTypeSupported('audio/webm;codecs=opus'));
      
      // Create MediaRecorder with proven working configuration
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      console.log('WebTalk: MediaRecorder created, state:', this.mediaRecorder.state);
      console.log('WebTalk: MediaRecorder mimeType:', this.mediaRecorder.mimeType);

      this.mediaRecorder.ondataavailable = (event) => {
        console.log('WebTalk: ondataavailable fired, data size:', event.data.size);
        if (event.data.size > 0) {
          console.log('WebTalk: Adding audio chunk, size:', event.data.size);
          this.audioChunks.push(event.data);
        } else {
          console.warn('WebTalk: Received empty audio chunk');
        }
      };

      this.mediaRecorder.onstop = () => {
        console.log('WebTalk: MediaRecorder stopped, total chunks:', this.audioChunks.length);
        this.processRecording();
      };

      this.mediaRecorder.onstart = () => {
        console.log('WebTalk: MediaRecorder started successfully');
      };

      this.mediaRecorder.onerror = (event) => {
        console.error('WebTalk: MediaRecorder error:', event.error);
        this.showError(`Recording error: ${event.error.message}`);
      };

      // Start recording with smaller chunks for better capture
      this.mediaRecorder.start(250); // Collect data every 250ms
      console.log('WebTalk: MediaRecorder.start() called');
      
      this.isRecording = true;
      this.updateUI('recording');
      this.updateStatus('🔴 Recording in progress... Speak now!');
      
      // Update transcription placeholder
      const transcriptionArea = this.recordingWindow.querySelector('.webtalk-transcription');
      if (transcriptionArea) {
        transcriptionArea.innerHTML = `
          <div class="transcription-placeholder">
            🔴 Recording in progress... Speak now!
          </div>
        `;
      }
      
    } catch (error) {
      console.error('WebTalk: Recording start failed:', error);
      this.showError(`Failed to start recording: ${error.message}`);
    }
  }

  // Stop recording
  stopRecording() {
    if (!this.isRecording || !this.mediaRecorder) {
      console.log('WebTalk: Cannot stop recording - not recording or no recorder');
      return;
    }

    console.log('WebTalk: Stopping recording...');
    this.isRecording = false;
    this.mediaRecorder.stop();
    this.updateUI('processing');
    this.updateStatus('⏳ Processing audio...');
  }

  // Process the recorded audio
  async processRecording() {
    if (this.audioChunks.length === 0) {
      console.log('WebTalk: No audio chunks recorded');
      this.updateStatus('No audio recorded - try holding the button longer');
      this.updateUI('ready');
      return;
    }

    // Check minimum recording duration (at least 1 second)
    const recordingDuration = this.recordingStartTime ? Date.now() - this.recordingStartTime : 0;
    if (recordingDuration < 1000) {
      console.log('WebTalk: Recording too short:', recordingDuration, 'ms');
      this.updateStatus('Recording too short - hold button for at least 1 second');
      this.updateUI('ready');
      return;
    }

    try {
      console.log('WebTalk: Processing', this.audioChunks.length, 'audio chunks');
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
      console.log('WebTalk: Audio blob created, size:', audioBlob.size);
      
      if (audioBlob.size === 0) {
        throw new Error('Audio blob is empty');
      }

      // Convert Blob to ArrayBuffer for Chrome messaging
      console.log('WebTalk: Converting blob to ArrayBuffer for transfer...');
      const arrayBuffer = await audioBlob.arrayBuffer();
      console.log('WebTalk: ArrayBuffer created, size:', arrayBuffer.byteLength);

      // Convert ArrayBuffer to Base64 string for more stable transfer
      console.log('WebTalk: Converting ArrayBuffer to Base64 string...');
      let base64Audio = '';
      try {
        const uint8Array = new Uint8Array(arrayBuffer);
        let binaryString = '';
        for (let i = 0; i < uint8Array.byteLength; i++) {
          binaryString += String.fromCharCode(uint8Array[i]);
        }
        base64Audio = btoa(binaryString);
        console.log('WebTalk: Base64 string created, length:', base64Audio.length);
      } catch (e) {
        console.error('WebTalk: Error converting ArrayBuffer to Base64:', e);
        this.showError(`Failed to prepare audio data: ${e.message}`);
        this.updateUI('ready');
        return;
      }

      // Send to background script for transcription
      console.log('WebTalk: Sending Base64 audio for transcription...');
      
      try {
        const response = await this.sendToBackground('transcribeAudio', { 
          audioDataB64: base64Audio, // Send as Base64
          audioType: 'audio/webm'
        });
        
        if (response && response.success) {
          console.log('WebTalk: Transcription successful:', response.data.transcription);
          this.displayTranscription(response.data.transcription);
          
          if (this.shouldAutoCopy) {
            // Auto-copy and close
            await this.copyTranscription();
            this.shouldAutoCopy = false;
          } else {
            this.updateStatus('✅ Transcription complete - Right-click to copy');
          }
        } else if (response && response.error) {
          console.error('WebTalk: Transcription failed:', response.error);
          this.showError(`Transcription failed: ${response.error}`);
        } else {
          console.error('WebTalk: Invalid response from background script:', response);
          this.showError('Communication error with background script. Try reloading the extension and server.');
        }
      } catch (backgroundError) {
        console.error('WebTalk: Background script communication error:', backgroundError);
        const errorMessage = backgroundError && backgroundError.message ? backgroundError.message : '';
        if (errorMessage.includes('Extension context invalidated')) {
          this.showError('Extension needs to be reloaded. Please refresh the page and reload the extension.');
        } else if (errorMessage.toLowerCase().includes('xtts-read-aloud')) {
          this.showError('Extension conflict detected. Try temporarily disabling the XTTS-Read-Aloud extension.');
        } else if (errorMessage.toLowerCase().includes('timeout')) {
          this.showError('Transcription timed out before the extension could respond. Try a shorter recording or restart WebTalk.');
        } else if (errorMessage) {
          this.showError(`Communication error: ${errorMessage}`);
        } else {
          this.showError('Communication error: Unknown background script issue.');
        }
      }
      
    } catch (error) {
      console.error('WebTalk: Processing error:', error);
      this.showError(`Error processing audio: ${error.message}`);
    }

    this.updateUI('ready');
  }

  // Display transcription in the window
  displayTranscription(text) {
    const transcriptionArea = this.recordingWindow.querySelector('.webtalk-transcription');
    transcriptionArea.innerHTML = `
      <div class="transcription-text">${text}</div>
      <div class="transcription-hint">Right-click to copy</div>
    `;
  }

  // Copy transcription to clipboard
  async copyTranscription() {
    const transcriptionText = this.recordingWindow.querySelector('.transcription-text');
    if (!transcriptionText) return;

    try {
      await navigator.clipboard.writeText(transcriptionText.textContent);
      this.updateStatus('📋 Copied to clipboard!');
      setTimeout(() => {
        this.closeRecordingWindow();
      }, 500);
    } catch (error) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = transcriptionText.textContent;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      
      this.updateStatus('📋 Copied to clipboard!');
      setTimeout(() => {
        this.closeRecordingWindow();
      }, 500);
    }
  }

  // Update UI state
  updateUI(state) {
    const controlsDiv = this.recordingWindow.querySelector('.webtalk-controls');
    
    switch (state) {
      case 'recording':
        // Already set up with stop buttons
        break;
      case 'processing':
        controlsDiv.className = 'webtalk-controls';
        controlsDiv.innerHTML = `
          <button class="webtalk-record-btn processing" disabled>
            <span class="record-icon">⏳</span>
            <span class="record-text">Processing...</span>
          </button>
        `;
        break;
      case 'ready':
        controlsDiv.className = 'webtalk-controls';
        controlsDiv.innerHTML = `
          <button class="webtalk-stop-btn" disabled>
            <span>✅</span>
            <span>Complete</span>
          </button>
        `;
        break;
    }
  }

  // Update status message
  updateStatus(message) {
    const statusElement = this.recordingWindow.querySelector('.webtalk-status');
    if (statusElement) {
      statusElement.textContent = message;
    }
  }

  // Show error message
  showError(message) {
    console.error('WebTalk: Error:', message);
    this.updateStatus(`❌ Error: ${message}`);
    const transcriptionArea = this.recordingWindow.querySelector('.webtalk-transcription');
    if (transcriptionArea) {
      transcriptionArea.innerHTML = `
        <div class="transcription-error">⚠️ ${message}</div>
        <div class="transcription-hint">Check browser console for details</div>
      `;
    }
  }

  // Show error dialog for server issues
  showErrorDialog(message) {
    alert(`WebTalk Error: ${message}\n\nPlease make sure:\n1. You've run install.bat\n2. You've run run.bat\n3. The server is running (check the popup for server status)`);
  }

  // Close the recording window
  closeRecordingWindow() {
    if (this.isRecording) {
      this.stopRecording();
    }

    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }

    // Remove event listeners
    if (this.outsideClickHandler) {
      document.removeEventListener('click', this.outsideClickHandler);
      this.outsideClickHandler = null;
    }

    if (this.keyHandler) {
      document.removeEventListener('keydown', this.keyHandler);
      this.keyHandler = null;
    }

    if (this.recordingWindow) {
      this.recordingWindow.remove();
      this.recordingWindow = null;
    }

    console.log('WebTalk: Recording window closed');
  }

  // Check server status
  async checkServerStatus() {
    return new Promise((resolve, reject) => {
      let timeoutId;
      let timedOut = false;
      try {
        timeoutId = setTimeout(() => {
          timedOut = true;
          timeoutId = null;
          reject(new Error('Server status check timeout'));
        }, 5000);

        chrome.runtime.sendMessage(
          { action: 'checkServerStatus' },
          (response) => {
            if (timedOut) {
              return;
            }

            if (timeoutId) {
              clearTimeout(timeoutId);
              timeoutId = null;
            }

            if (chrome.runtime.lastError) {
              console.error('WebTalk: Chrome runtime error during server check:', chrome.runtime.lastError);
              reject(new Error(chrome.runtime.lastError.message));
              return;
            }

            if (response === undefined) {
              console.error('WebTalk: No response from background script during server check');
              reject(new Error('Background script not responding'));
              return;
            }

            resolve(response);
          }
        );
      } catch (error) {
        if (timeoutId) {
          clearTimeout(timeoutId);
          timeoutId = null;
        }
        console.error('WebTalk: Error checking server status:', error);
        reject(error);
      }
    });
  }

  // Send message to background script
  async sendToBackground(action, data) {
    return new Promise((resolve, reject) => {
      let timeoutId;
      let timedOut = false;
      try {
        const timeoutDuration = action === 'transcribeAudio' ? 45000 : 15000;
        timeoutId = setTimeout(() => {
          timedOut = true;
          timeoutId = null;
          reject(new Error('Background script response timeout. The request may still be processing.'));
        }, timeoutDuration);

        chrome.runtime.sendMessage(
          { action, ...data },
          (response) => {
            if (timedOut) {
              return;
            }

            if (timeoutId) {
              clearTimeout(timeoutId);
              timeoutId = null;
            }

            if (chrome.runtime.lastError) {
              console.error('WebTalk: Chrome runtime error:', chrome.runtime.lastError);
              reject(new Error(chrome.runtime.lastError.message));
              return;
            }

            if (response === undefined) {
              console.error('WebTalk: Background script did not respond');
              reject(new Error('Background script did not respond. The extension may need to be reloaded.'));
              return;
            }

            resolve(response);
          }
        );
      } catch (error) {
        if (timeoutId) {
          clearTimeout(timeoutId);
          timeoutId = null;
        }
        console.error('WebTalk: Error sending message to background:', error);
        reject(error);
      }
    });
  }
}

// Global recorder instance
const webTalkRecorder = new WebTalkRecorder();

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('WebTalk: Received message:', request.action);
  
  if (request.action === 'showRecordingWindow') {
    webTalkRecorder.showRecordingWindow(request.clickX, request.clickY);
  }
  
  sendResponse({ success: true });
  return true;
}); 
