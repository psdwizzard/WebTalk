// Simple WebTalk Content Script Test
console.log('WebTalk: Content script loaded successfully on:', window.location.href);

// Test if we can access Chrome APIs
if (typeof chrome !== 'undefined' && chrome.runtime) {
  console.log('WebTalk: Chrome runtime available');
} else {
  console.error('WebTalk: Chrome runtime NOT available');
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('WebTalk: Received message from background:', request);
  
  if (request.action === 'showRecordingWindow') {
    console.log('WebTalk: Showing recording window...');
    
    // Create a simple test popup
    const popup = document.createElement('div');
    popup.id = 'webtalk-test-popup';
    popup.style.cssText = `
      position: fixed;
      top: 50px;
      right: 50px;
      width: 300px;
      height: 200px;
      background: white;
      border: 2px solid #007acc;
      border-radius: 8px;
      padding: 20px;
      z-index: 10000;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      font-family: Arial, sans-serif;
    `;
    
    popup.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 10px;">🎤 WebTalk Test</div>
      <div>✅ Content script is working!</div>
      <div>✅ Background communication OK</div>
      <div style="margin-top: 10px; font-size: 12px; color: #666;">
        Click: ${request.clickX}, ${request.clickY}<br>
        URL: ${window.location.hostname}
      </div>
      <button onclick="document.getElementById('webtalk-test-popup').remove()" 
              style="margin-top: 15px; padding: 5px 10px; cursor: pointer;">
        Close
      </button>
    `;
    
    // Remove any existing popup
    const existing = document.getElementById('webtalk-test-popup');
    if (existing) {
      existing.remove();
    }
    
    document.body.appendChild(popup);
    console.log('WebTalk: Test popup created and added to page');
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (popup.parentElement) {
        popup.remove();
        console.log('WebTalk: Test popup auto-removed');
      }
    }, 10000);
  }
  
  sendResponse({ success: true, message: 'Content script received message' });
  return true;
}); 