// extension/background.js

const DEBUG = true; // set to false once everything is confirmed working

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeText') {
    if (DEBUG) console.log('[Scamlex:bg] received analyzeText, calling backend...', request.payload);

    fetch('http://127.0.0.1:8000/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request.payload)
    })
      .then((res) => {
        if (DEBUG) console.log('[Scamlex:bg] backend HTTP status:', res.status);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (DEBUG) console.log('[Scamlex:bg] backend response body:', data);
        sendResponse({
          isScam: data.isScam || false,
          score: data.score || 0,
          level: data.level || 'LOW',
          message: data.message || '',
          reasons: data.reasons || [],
          flaggedTexts: data.flaggedTexts || []
        });
      })
      .catch((err) => {
        console.warn('[Scamlex:bg] Fetch Error:', err.message);
        sendResponse({ 
          isScam: false, 
          error: err.message,
          reasons: [],
          flaggedTexts: []
        });
      });

    return true; // Keep message channel open for async response
  }
});

chrome.runtime.onConnect.addListener((port) => {
  if (port.name === 'Scamlex-heartbeat') {
    // keeping connection alive
  }
});

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(['isConnected'], (result) => {
    if (result.isConnected === undefined) {
      chrome.storage.local.set({ isConnected: true });
    }
  });
});
