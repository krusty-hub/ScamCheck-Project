import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);

  await page.goto('http://localhost:5173/auth', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#email');

  // Let's get object ID for window and document
  const windowObj = await cdp.send('Runtime.evaluate', { expression: 'window' });
  const docObj = await cdp.send('Runtime.evaluate', { expression: 'document' });
  const bodyObj = await cdp.send('Runtime.evaluate', { expression: 'document.body' });
  const emailObj = await cdp.send('Runtime.evaluate', { expression: 'document.getElementById("email")' });

  const winListeners = await cdp.send('DOMDebugger.getEventListeners', { objectId: windowObj.result.objectId });
  const docListeners = await cdp.send('DOMDebugger.getEventListeners', { objectId: docObj.result.objectId });
  const bodyListeners = await cdp.send('DOMDebugger.getEventListeners', { objectId: bodyObj.result.objectId });
  const emailListeners = await cdp.send('DOMDebugger.getEventListeners', { objectId: emailObj.result.objectId });

  console.log('WINDOW LISTENERS:', winListeners.listeners.map(l => ({ type: l.type, scriptId: l.scriptId, lineNumber: l.lineNumber })));
  console.log('DOCUMENT LISTENERS:', docListeners.listeners.map(l => ({ type: l.type, scriptId: l.scriptId, lineNumber: l.lineNumber })));
  console.log('BODY LISTENERS:', bodyListeners.listeners.map(l => ({ type: l.type, scriptId: l.scriptId, lineNumber: l.lineNumber })));
  console.log('EMAIL LISTENERS:', emailListeners.listeners.map(l => ({ type: l.type, scriptId: l.scriptId, lineNumber: l.lineNumber })));

  await browser.close();
})().catch(err => {
  console.error(err);
  process.exit(1);
});
