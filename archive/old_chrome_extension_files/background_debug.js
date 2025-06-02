// WebTalk Background Script with Enhanced Debugging
console.log('WebTalk Background: Service Worker Started');

// Create context menu on startup
chrome.runtime.onStartup.addListener(() => {
  console.log('WebTalk Background: onStartup triggered');
  createContextMenu();
});

chrome.runtime.onInstalled.addListener(() => {
  console.log('WebTalk Background: onInstalled triggered');
  createContextMenu();
});

function createContextMenu() {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "webTalkRecord",
      title: "🎤 Record with WebTalk",
      contexts: ["page", "selection", "editable"]
    });
    console.log('WebTalk Background: Context menu created');
  });
}

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  console.log('WebTalk Background: Context menu clicked!', info);
  
  if (info.menuItemId === "webTalkRecord") {
    console.log('WebTalk Background: Correct menu item clicked, tab ID:', tab.id);
    
    // Send message to content script to show recording window
    chrome.tabs.sendMessage(tab.id, {
      action: "showRecordingWindow",
      clickX: info.pageX || 100,
      clickY: info.pageY || 100
    }, (response) => {
      if (chrome.runtime.lastError) {
        console.error('WebTalk Background: Failed to send message to content script:', chrome.runtime.lastError.message);
      } else {
        console.log('WebTalk Background: Message sent successfully to content script:', response);
      }
    });
  }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('WebTalk Background: Received message:', request.action);
  
  // Keep track of whether we've already sent a response
  let responseSent = false;
  const safeSendResponse = (response) => {
    if (!responseSent) {
      responseSent = true;
      console.log('WebTalk Background: Sending response:', response);
      try {
        sendResponse(response);
      } catch (error) {
        console.error('WebTalk Background: Error sending response:', error);
      }
    }
  };
  
  if (request.action === "checkServerStatus") {
    console.log('WebTalk Background: Checking server status...');
    
    // Add a safety timeout
    const timeoutId = setTimeout(() => {
      console.error('WebTalk Background: Server check timeout');
      safeSendResponse({ 
        success: false, 
        error: "Server check timeout" 
      });
    }, 6000);
    
    fetch("http://localhost:9090/health", {
      method: "GET",
      signal: AbortSignal.timeout(5000) // 5 second timeout
    })
      .then(response => {
        clearTimeout(timeoutId);
        if (!response.ok) {
          throw new Error(`Server responded with status ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('WebTalk Background: Server health check successful');
        safeSendResponse({ success: true, data });
      })
      .catch(error => {
        clearTimeout(timeoutId);
        console.error('WebTalk Background: Server health check failed:', error);
        safeSendResponse({ 
          success: false, 
          error: "Whisper server not running. Please run run.bat first." 
        });
      });
    return true; // Keep message channel open for async response
  }
  
  if (request.action === "transcribeAudio") {
    console.log('WebTalk Background: Starting transcription...');
    console.log('WebTalk Background: Received raw request object (now expecting Base64):', JSON.stringify(request, null, 2));
    
    console.log('WebTalk Background: audioType from request:', request.audioType);
    console.log('WebTalk Background: audioDataB64 present:', !!request.audioDataB64);
    console.log('WebTalk Background: audioDataB64 length:', request.audioDataB64?.length);

    if (!request.audioDataB64 || typeof request.audioDataB64 !== 'string' || request.audioDataB64.length === 0) {
      console.error('❌ WebTalk Background: No Base64 audio data provided or it is empty.');
      safeSendResponse({ 
        success: false, 
        error: "No Base64 audio data provided or it was empty." 
      });
      return true;
    }
    
    // Add a safety timeout for the entire transcription process
    const timeoutId = setTimeout(() => {
      console.error('WebTalk Background: Transcription process timeout (Base64)');
      safeSendResponse({ 
        success: false, 
        error: "Transcription timeout - try shorter recordings (Base64 path)" 
      });
    }, 45000); // Increased timeout slightly for Base64 decoding
    
    try {
      // Decode Base64 to Uint8Array
      console.log('🔄 WebTalk Background: Decoding Base64 audio data...');
      let decodedAudioBytes;
      try {
        const binaryString = atob(request.audioDataB64);
        decodedAudioBytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          decodedAudioBytes[i] = binaryString.charCodeAt(i);
        }
        console.log('✅ WebTalk Background: Base64 decoded, byte length:', decodedAudioBytes.byteLength);
      } catch (e) {
        console.error('❌ WebTalk Background: Error decoding Base64 string:', e);
        clearTimeout(timeoutId);
        safeSendResponse({ success: false, error: `Failed to decode audio data: ${e.message}` });
        return true;
      }

      if (!decodedAudioBytes || decodedAudioBytes.byteLength === 0) {
        console.error('❌ WebTalk Background: Decoded audio data is empty.');
        clearTimeout(timeoutId);
        safeSendResponse({ success: false, error: 'Decoded audio data is empty.' });
        return true;
      }
      
      const audioBlob = new Blob([decodedAudioBytes], { type: request.audioType || 'audio/webm' });
      console.log('🎵 WebTalk Background: Blob created from decoded Base64, size:', audioBlob.size, 'bytes');
      
      // Debug the blob contents if it's suspiciously small
      if (audioBlob.size < 1000 && audioBlob.size > 0) { // only log if not zero but small
        console.error('⚠️ WebTalk Background: Blob too small! Only', audioBlob.size, 'bytes');
        audioBlob.arrayBuffer().then(arrayBuffer => {
          const uint8Array = new Uint8Array(arrayBuffer);
          console.log('🔍 WebTalk Background: Blob content (first 20 bytes):', Array.from(uint8Array.slice(0, 20)));
          console.log('🔍 WebTalk Background: Blob content (last 20 bytes):', Array.from(uint8Array.slice(-20)));
        });
      }
      
      // Forward audio to Whisper server
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      console.log('📤 WebTalk Background: Sending request to server...');
      
      fetch("http://localhost:9090/transcribe", {
        method: "POST",
        body: formData,
        signal: AbortSignal.timeout(30000) // 30 second timeout for transcription
      })
      .then(response => {
        console.log('📥 WebTalk Background: Server response status:', response.status);
        if (!response.ok) {
          return response.text().then(text => {
            throw new Error(`Server error ${response.status}: ${text}`);
          });
        }
        return response.json();
      })
      .then(data => {
        clearTimeout(timeoutId);
        console.log('✅ WebTalk Background: Transcription successful:', data.transcription?.substring(0, 50) + '...');
        safeSendResponse({ success: true, data });
      })
      .catch(error => {
        clearTimeout(timeoutId);
        console.error('❌ WebTalk Background: Transcription failed:', error);
        let errorMessage = error.message;
        
        if (error.name === 'AbortError') {
          errorMessage = 'Transcription timeout - audio may be too long or server is overloaded';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
          errorMessage = 'Cannot connect to Whisper server. Make sure run.bat is running.';
        } else if (error.message.includes('Invalid audio file type')) {
          errorMessage = 'Audio format not supported by server - try speaking longer';
        } else if (error.message.includes('Server error')) {
          errorMessage = `Server error: ${error.message}`;
        }
        
        safeSendResponse({ 
          success: false, 
          error: errorMessage 
        });
      });
    } catch (error) {
      clearTimeout(timeoutId);
      console.error('💥 WebTalk Background: Unexpected error:', error);
      safeSendResponse({ 
        success: false, 
        error: `Unexpected error: ${error.message}` 
      });
    }
    
    return true; // Keep message channel open for async response
  }
  
  // Always send a response for unknown actions
  console.warn('WebTalk Background: Unknown action:', request.action);
  safeSendResponse({ success: false, error: 'Unknown action' });
  return false;
}); 