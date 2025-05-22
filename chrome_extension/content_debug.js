// WebTalk Debug Content Script
console.log('WebTalk Debug: Script loaded');

let debugRecorder = null;

// Test microphone access immediately when script loads
async function testMicrophone() {
  console.log('WebTalk Debug: Testing microphone access...');
  
  try {
    // Get devices
    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioDevices = devices.filter(d => d.kind === 'audioinput');
    console.log('WebTalk Debug: Audio devices found:', audioDevices.length);
    
    // Test getUserMedia
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.log('WebTalk Debug: Stream obtained:', stream);
    console.log('WebTalk Debug: Stream active:', stream.active);
    
    const tracks = stream.getAudioTracks();
    console.log('WebTalk Debug: Audio tracks:', tracks.length);
    if (tracks.length > 0) {
      console.log('WebTalk Debug: Track details:', {
        enabled: tracks[0].enabled,
        readyState: tracks[0].readyState,
        muted: tracks[0].muted
      });
    }
    
    // Test MediaRecorder
    console.log('WebTalk Debug: Testing MediaRecorder...');
    console.log('WebTalk Debug: Supports webm/opus:', MediaRecorder.isTypeSupported('audio/webm;codecs=opus'));
    console.log('WebTalk Debug: Supports webm:', MediaRecorder.isTypeSupported('audio/webm'));
    
    const recorder = new MediaRecorder(stream);
    console.log('WebTalk Debug: MediaRecorder created, mimeType:', recorder.mimeType);
    
    let chunks = [];
    recorder.ondataavailable = (event) => {
      console.log('WebTalk Debug: Data available, size:', event.data.size);
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };
    
    recorder.onstop = () => {
      console.log('WebTalk Debug: Recording stopped, chunks:', chunks.length);
      const blob = new Blob(chunks, { type: recorder.mimeType });
      console.log('WebTalk Debug: Final blob size:', blob.size);
      
      // Cleanup
      stream.getTracks().forEach(track => track.stop());
    };
    
    recorder.onstart = () => {
      console.log('WebTalk Debug: Recording started');
    };
    
    // Store for manual testing
    debugRecorder = { recorder, stream, chunks };
    
    console.log('WebTalk Debug: Microphone test complete - ready for manual recording test');
    console.log('WebTalk Debug: Use window.startDebugRecording() and window.stopDebugRecording() to test');
    
    // Make functions available globally for testing
    window.startDebugRecording = () => {
      console.log('WebTalk Debug: Starting manual recording...');
      chunks.length = 0; // Clear previous chunks
      recorder.start(250);
    };
    
    window.stopDebugRecording = () => {
      console.log('WebTalk Debug: Stopping manual recording...');
      recorder.stop();
    };
    
  } catch (error) {
    console.error('WebTalk Debug: Microphone test failed:', error);
  }
}

// Create a simple UI for testing
function createDebugUI() {
  console.log('WebTalk Debug: Creating test UI...');
  
  const debugPanel = document.createElement('div');
  debugPanel.id = 'webtalk-debug-panel';
  debugPanel.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    width: 300px;
    padding: 15px;
    background: #f0f0f0;
    border: 2px solid #007acc;
    border-radius: 8px;
    z-index: 10000;
    font-family: Arial, sans-serif;
    font-size: 12px;
  `;
  
  debugPanel.innerHTML = `
    <div style="font-weight: bold; margin-bottom: 10px;">🔧 WebTalk Debug Panel</div>
    <button onclick="window.startDebugRecording()" style="margin: 5px; padding: 5px 10px;">Start Recording</button>
    <button onclick="window.stopDebugRecording()" style="margin: 5px; padding: 5px 10px;">Stop Recording</button>
    <button onclick="document.getElementById('webtalk-debug-panel').remove()" style="margin: 5px; padding: 5px 10px;">Close</button>
    <div id="debug-status" style="margin-top: 10px; font-size: 11px;">Ready for testing</div>
  `;
  
  document.body.appendChild(debugPanel);
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('WebTalk Debug: Received message:', request);
  
  if (request.action === 'showRecordingWindow') {
    console.log('WebTalk Debug: Showing debug panel instead of recording window');
    createDebugUI();
    testMicrophone();
  }
  
  sendResponse({ success: true });
  return true;
}); 