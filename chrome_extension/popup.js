// WebTalk Popup Script
// Handles popup interactions and server status checking

document.addEventListener('DOMContentLoaded', async () => {
  const statusIndicator = document.getElementById('statusIndicator');
  const statusText = document.getElementById('statusText');
  const testServerBtn = document.getElementById('testServer');
  const openSettingsBtn = document.getElementById('openSettings');

  // Check server status on popup open
  await checkServerStatus();

  // Test server button click
  testServerBtn.addEventListener('click', async () => {
    testServerBtn.textContent = 'Testing...';
    testServerBtn.disabled = true;
    
    await checkServerStatus();
    
    testServerBtn.textContent = 'Test Server';
    testServerBtn.disabled = false;
  });

  // Settings button click
  openSettingsBtn.addEventListener('click', () => {
    chrome.tabs.create({ url: 'chrome://extensions/?id=' + chrome.runtime.id });
    window.close();
  });

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
          console.log(`WebTalk Popup: Found server on port ${port}`);
          return port;
        }
      } catch (error) {
        // Continue to next port
      }
    }
    
    console.log('WebTalk Popup: No server found on common ports, using default 8000');
    return 8000;
  }

  // Check server status function
  async function checkServerStatus() {
    try {
      statusIndicator.textContent = '🟡';
      statusText.textContent = 'Checking server...';
      statusText.className = 'status-checking';

      const port = await discoverServerPort();
      const response = await fetch(`http://localhost:${port}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });

      if (response.ok) {
        const data = await response.json();
        
        statusIndicator.textContent = '🟢';
        statusIndicator.className = 'status-indicator online';
        statusText.textContent = `Server online (${data.device}) - Port ${port}`;
        statusText.className = 'status-online';

        // Show additional info if available
        if (data.model) {
          statusText.textContent += ` - ${data.model}`;
        }
      } else {
        throw new Error('Server responded with error');
      }
    } catch (error) {
      statusIndicator.textContent = '🔴';
      statusIndicator.className = 'status-indicator offline';
      statusText.textContent = 'Server offline - Run run.bat first';
      statusText.className = 'status-offline';
    }
  }

  // Update server status periodically
  setInterval(checkServerStatus, 10000); // Check every 10 seconds
}); 