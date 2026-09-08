import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('console', msg => console.log(`[PAGE LOG] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR]: ${err.message}`));

  console.log('Navigating to http://localhost:5173/auth ...');
  await page.goto('http://localhost:5173/auth', { waitUntil: 'domcontentloaded' });
  console.log('Waiting for selector #email...');
  await page.waitForSelector('#email', { timeout: 10000 });
  console.log('Found #email!');

  const cdp = await context.newCDPSession(page);
  await cdp.send('Debugger.enable');

  cdp.on('Debugger.paused', (params) => {
    console.log('=== Debugger PAUSED! Reason:', params.reason, '===');
    console.log('Call stack:');
    for (let i = 0; i < Math.min(params.callFrames.length, 25); i++) {
      const f = params.callFrames[i];
      console.log(`  at ${f.functionName || '(anonymous)'} (${f.url}:${f.location.lineNumber + 1}:${f.location.columnNumber + 1})`);
    }
    process.exit(0);
  });

  console.log('Setting timeout to pause in 500ms...');
  setTimeout(async () => {
    console.log('Calling Debugger.pause...');
    try {
      await cdp.send('Debugger.pause');
    } catch (e) {
      console.error('Failed to pause:', e.message);
    }
  }, 500);

  console.log('Dispatching input on #email...');
  await page.evaluate(() => {
    const el = document.getElementById('email');
    el.value = 'a';
    el.dispatchEvent(new Event('input', { bubbles: true }));
  });

  console.log('If you see this, evaluate did not block!');
  await browser.close();
})().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});
