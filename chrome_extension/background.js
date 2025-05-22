// WebTalk Background Script
// Handles context menu creation and communication with content scripts

// Create context menu when extension is installed
chrome.runtime.onInstalled.addListener(() => {
  console.log('WebTalk Background: Extension installed/reloaded');
  chrome.contextMenus.create({
    id: "webTalkRecord",
    title: "🎤 Start WebTalk Recording",
    contexts: ["page", "selection", "editable"]
  });
  console.log('WebTalk Background: Context menu created');
});

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
        console.log('WebTalk Background: Attempting to inject content script...');
        
        // Try to inject the content script if it's not loaded
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['content_simple.js']
        }).then(() => {
          console.log('WebTalk Background: Content script injected, retrying message...');
          // Small delay then retry
          setTimeout(() => {
            chrome.tabs.sendMessage(tab.id, {
              action: "showRecordingWindow",
              clickX: info.pageX || 100,
              clickY: info.pageY || 100
            }, (retryResponse) => {
              if (chrome.runtime.lastError) {
                console.error('WebTalk Background: Retry also failed:', chrome.runtime.lastError.message);
              } else {
                console.log('WebTalk Background: Retry successful!');
              }
            });
          }, 100);
        }).catch(error => {
          console.error('WebTalk Background: Failed to inject content script:', error);
        });
      } else {
        console.log('WebTalk Background: Message sent successfully to content script:', response);
      }
    });
  } else {
    console.log('WebTalk Background: Unknown menu item clicked:', info.menuItemId);
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
    
    fetch("http://localhost:8000/health", {
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
    console.log('WebTalk Background: Starting transcription, audio data size:', request.audioData?.byteLength);
    
    if (!request.audioData) {
      console.error('WebTalk Background: No audio data provided');
      safeSendResponse({ 
        success: false, 
        error: "No audio data provided" 
      });
      return false;
    }
    
    // Add a safety timeout for the entire transcription process
    const timeoutId = setTimeout(() => {
      console.error('WebTalk Background: Transcription process timeout');
      safeSendResponse({ 
        success: false, 
        error: "Transcription timeout - try shorter recordings" 
      });
    }, 35000); // 35 second safety net
    
        try {      // Debug the received ArrayBuffer      console.log('WebTalk Background: Received audioData type:', typeof request.audioData);      console.log('WebTalk Background: Received audioData instanceof ArrayBuffer:', request.audioData instanceof ArrayBuffer);      console.log('WebTalk Background: Received audioData byteLength:', request.audioData?.byteLength);            // Convert ArrayBuffer back to Blob for FormData      console.log('WebTalk Background: Converting ArrayBuffer to Blob...');      const audioBlob = new Blob([request.audioData], { type: request.audioType || 'audio/webm' });      console.log('WebTalk Background: Blob created, size:', audioBlob.size);            // Debug the blob contents      if (audioBlob.size < 100) {        console.error('WebTalk Background: ⚠️  Blob too small! Only', audioBlob.size, 'bytes');        const arrayBuffer = await audioBlob.arrayBuffer();        const uint8Array = new Uint8Array(arrayBuffer);        console.log('WebTalk Background: Blob content (first 50 bytes):', Array.from(uint8Array.slice(0, 50)));      }
      
      // Forward audio to Whisper server
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      console.log('WebTalk Background: Sending request to server...');
      
      fetch("http://localhost:8000/transcribe", {
        method: "POST",
        body: formData,
        signal: AbortSignal.timeout(30000) // 30 second timeout for transcription
      })
      .then(response => {
        console.log('WebTalk Background: Server response status:', response.status);
        if (!response.ok) {
          return response.text().then(text => {
            throw new Error(`Server error ${response.status}: ${text}`);
          });
        }
        return response.json();
      })
      .then(data => {
        clearTimeout(timeoutId);
        console.log('WebTalk Background: Transcription successful:', data.transcription?.substring(0, 50) + '...');
        safeSendResponse({ success: true, data });
      })
      .catch(error => {
        clearTimeout(timeoutId);
        console.error('WebTalk Background: Transcription failed:', error);
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
      console.error('WebTalk Background: Unexpected error:', error);
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