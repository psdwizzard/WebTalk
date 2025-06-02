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
          files: ['content.js']
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

// Server configuration
let serverConfig = {
  port: 8000,
  host: 'localhost'
};

// Try to discover the correct server port
async function discoverServerPort() {
  const commonPorts = [8000, 8001, 8080, 5000, 3000];
  
  for (const port of commonPorts) {
    try {
      const response = await fetch(`http://localhost:${port}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000)
      });
      
      if (response.ok) {
        console.log(`WebTalk Background: Found server on port ${port}`);
        serverConfig.port = port;
        
        // Try to get the actual config to confirm the port
        try {
          const configResponse = await fetch(`http://localhost:${port}/config`, {
            method: 'GET',
            signal: AbortSignal.timeout(2000)
          });
          
          if (configResponse.ok) {
            const config = await configResponse.json();
            if (config.server_port && config.server_port !== port) {
              console.log(`WebTalk Background: Server config shows port ${config.server_port}, but found on ${port}`);
              // Use the port we actually found the server on
            }
          }
        } catch (configError) {
          console.log('WebTalk Background: Could not fetch config, using discovered port');
        }
        
        return port;
      }
    } catch (error) {
      // Continue to next port
    }
  }
  
  console.log('WebTalk Background: No server found on common ports, using default 8000');
  return 8000;
}

// Get server URL
function getServerUrl() {
  return `http://${serverConfig.host}:${serverConfig.port}`;
}

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
    }, 8000);
    
    // Try to discover the server port first
    discoverServerPort().then(port => {
      serverConfig.port = port;
      return fetch(`${getServerUrl()}/health`, {
        method: "GET",
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });
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
    console.log('WebTalk Background: Starting transcription');
    
    if (!request.audioDataB64) {
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
    
    try {
      // Convert Base64 back to binary data
      console.log('WebTalk Background: Converting Base64 to binary data...');
      const binaryString = atob(request.audioDataB64);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Create blob from binary data
      const audioBlob = new Blob([bytes], { type: request.audioType || 'audio/webm' });
      console.log('WebTalk Background: Blob created, size:', audioBlob.size);
      
      // Forward audio to Whisper server
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      console.log('WebTalk Background: Sending request to server...');
      
      fetch(`${getServerUrl()}/transcribe`, {
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