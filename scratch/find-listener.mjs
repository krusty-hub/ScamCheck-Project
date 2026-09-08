import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);

  await cdp.send('Debugger.enable');

  let scripts = {};
  cdp.on('Debugger.scriptParsed', (s) => {
    scripts[s.scriptId] = { url: s.url, length: s.length };
  });

  await page.goto('http://localhost:5173/auth', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#email');

  const windowObj = await cdp.send('Runtime.evaluate', { expression: 'window' });
  const winListeners = await cdp.send('DOMDebugger.getEventListeners', { objectId: windowObj.result.objectId });
  const clickListeners = winListeners.listeners.filter(l => l.type === 'click' || l.type === 'mouseup');

  for (const l of clickListeners) {
    const s = scripts[l.scriptId];
    console.log(`Listener ${l.type} at line ${l.lineNumber} scriptId ${l.lineNumber}:`, s?.url);
    const src = await cdp.send('Debugger.getScriptSource', { scriptId: l.scriptId });
    const lines = src.scriptSource.split('\n');
    console.log(`Snippet around line ${l.lineNumber}:`);
    console.log(lines.slice(Math.max(0, l.lineNumber - 5), l.lineNumber + 15).join('\n'));
  }

  await browser.close();
})().catch(err => {
  console.error(err);
  process.exit(1);
});
