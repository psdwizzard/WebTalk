// WebTalk Debug Content Script v2
console.log('WebTalk Debug v2: Script loaded');

let debugRecorder = null;
let testResults = {};

// Auto-test recording with different configurations
async function autoTestRecording() {
  console.log('WebTalk Debug v2: Starting automatic recording test...');
  
  try {
    // Get stream
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    console.log('WebTalk Debug v2: Stream obtained for auto-test');
    
    // Test different MediaRecorder configurations
    const configs = [
      { mimeType: 'audio/webm;codecs=opus', name: 'webm-opus' },
      { mimeType: 'audio/webm', name: 'webm-default' },
      { mimeType: undefined, name: 'browser-default' }
    ];
    
    for (let config of configs) {
      console.log(`WebTalk Debug v2: Testing config: ${config.name}`);
      
      try {
        const recorder = config.mimeType ? 
          new MediaRecorder(stream, { mimeType: config.mimeType }) :
          new MediaRecorder(stream);
          
        console.log(`WebTalk Debug v2: ${config.name} - Created recorder, mimeType: "${recorder.mimeType}"`);
        
        // Test a quick recording
        await testQuickRecording(recorder, config.name);
        
      } catch (error) {
        console.error(`WebTalk Debug v2: ${config.name} failed:`, error);
      }
    }
    
    // Cleanup
    stream.getTracks().forEach(track => track.stop());
    
  } catch (error) {
    console.error('WebTalk Debug v2: Auto-test failed:', error);
  }
}

// Test a quick 2-second recording
function testQuickRecording(recorder, configName) {
  return new Promise((resolve) => {
    let chunks = [];
    
    recorder.ondataavailable = (event) => {
      console.log(`WebTalk Debug v2: ${configName} - Data chunk: ${event.data.size} bytes`);
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };
    
    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
      console.log(`WebTalk Debug v2: ${configName} - Final blob: ${blob.size} bytes`);
      testResults[configName] = {
        mimeType: recorder.mimeType,
        chunks: chunks.length,
        totalSize: blob.size
      };
      resolve();
    };
    
    recorder.onstart = () => {
      console.log(`WebTalk Debug v2: ${configName} - Recording started`);
    };
    
    recorder.onerror = (event) => {
      console.error(`WebTalk Debug v2: ${configName} - Error:`, event.error);
      resolve();
    };
    
    // Start recording
    recorder.start(250);
    
    // Stop after 2 seconds
    setTimeout(() => {
      if (recorder.state === 'recording') {
        console.log(`WebTalk Debug v2: ${configName} - Stopping after 2 seconds`);
        recorder.stop();
      }
    }, 2000);
  });
}

// Create improved debug UI (no inline handlers)
function createDebugUI() {
  console.log('WebTalk Debug v2: Creating improved test UI...');
  
  const debugPanel = document.createElement('div');
  debugPanel.id = 'webtalk-debug-panel-v2';
  debugPanel.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    width: 350px;
    padding: 15px;
    background: #f0f0f0;
    border: 2px solid #007acc;
    border-radius: 8px;
    z-index: 10000;
    font-family: Arial, sans-serif;
    font-size: 12px;
    max-height: 80vh;
    overflow-y: auto;
  `;
  
  debugPanel.innerHTML = `
    <div style="font-weight: bold; margin-bottom: 10px;">🔧 WebTalk Debug Panel v2</div>
    <div id="test-status" style="margin: 10px 0; padding: 8px; background: #e0e0e0; border-radius: 4px;">
      Running automatic tests...
    </div>
    <div id="test-results" style="margin: 10px 0; font-size: 11px;"></div>
    <button id="close-debug" style="margin: 5px; padding: 5px 10px;">Close</button>
    <button id="rerun-test" style="margin: 5px; padding: 5px 10px;">Re-run Test</button>
  `;
  
  document.body.appendChild(debugPanel);
  
  // Add event listeners (proper way, no CSP issues)
  document.getElementById('close-debug').addEventListener('click', () => {
    debugPanel.remove();
  });
  
  document.getElementById('rerun-test').addEventListener('click', () => {
    document.getElementById('test-status').textContent = 'Re-running tests...';
    document.getElementById('test-results').innerHTML = '';
    testResults = {};
    autoTestRecording().then(() => {
      displayResults();
    });
  });
  
  // Run auto test and display results
  autoTestRecording().then(() => {
    displayResults();
  });
}

// Display test results in the UI
function displayResults() {
  const statusEl = document.getElementById('test-status');
  const resultsEl = document.getElementById('test-results');
  
  if (!statusEl || !resultsEl) return;
  
  statusEl.textContent = 'Tests completed! Check console for details.';
  
  let resultsHTML = '<div style="font-weight: bold;">Test Results:</div>';
  
  for (let [configName, result] of Object.entries(testResults)) {
    const success = result.totalSize > 100;
    const statusIcon = success ? '✅' : '❌';
    const statusColor = success ? 'green' : 'red';
    
    resultsHTML += `
      <div style="margin: 5px 0; padding: 5px; background: white; border-radius: 3px;">
        <span style="color: ${statusColor};">${statusIcon}</span> 
        <strong>${configName}</strong><br>
        MimeType: "${result.mimeType}"<br>
        Chunks: ${result.chunks}, Size: ${result.totalSize} bytes
      </div>
    `;
  }
  
  resultsEl.innerHTML = resultsHTML;
  
  // Log summary
  console.log('WebTalk Debug v2: Test Summary:', testResults);
  
  // Find the best working configuration
  const workingConfigs = Object.entries(testResults).filter(([name, result]) => result.totalSize > 100);
  if (workingConfigs.length > 0) {
    console.log('WebTalk Debug v2: ✅ Working configurations found:', workingConfigs.map(([name]) => name));
  } else {
    console.log('WebTalk Debug v2: ❌ No working configurations found - all produced small files');
  }
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('WebTalk Debug v2: Received message:', request);
  
  if (request.action === 'showRecordingWindow') {
    console.log('WebTalk Debug v2: Starting comprehensive debug test');
    
    // Remove any existing debug panels
    const existing = document.getElementById('webtalk-debug-panel-v2');
    if (existing) existing.remove();
    
    createDebugUI();
  }
  
  sendResponse({ success: true });
  return true;
}); 