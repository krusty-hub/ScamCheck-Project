import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);

  page.on('console', msg => console.log(`[PAGE LOG] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR]: ${err.message}`));

  await cdp.send('Debugger.enable');

  cdp.on('Debugger.paused', async (params) => {
    console.log('\n================== Debugger PAUSED! ==================');
    console.log('Reason:', params.reason);
    console.log('Call stack (top 20 frames):');
    for (let i = 0; i < Math.min(params.callFrames.length, 20); i++) {
      const f = params.callFrames[i];
      console.log(`  [Frame ${i}] ${f.functionName || '(anonymous)'}`);
      console.log(`    Location: ${f.url}:${f.location.lineNumber + 1}:${f.location.columnNumber + 1}`);
      if (i === 0 && f.callFrameId) {
        try {
          const evalRes = await cdp.send('Debugger.evaluateOnCallFrame', {
            callFrameId: f.callFrameId,
            expression: 'typeof window !== "undefined" ? "in-browser" : "unknown"'
          });
          console.log(`    Scope check:`, evalRes.result.value);
        } catch (e) {}
      }
    }
    console.log('======================================================\n');
    await browser.close();
    process.exit(0);
  });

  await page.goto('http://localhost:5173/auth', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#email');

  const rect = await page.evaluate(() => {
    const r = document.getElementById('email').getBoundingClientRect();
    return { x: r.x + 10, y: r.y + 10 };
  });

  await page.mouse.move(rect.x, rect.y);
  await page.mouse.down();

  console.log('Mouse down complete. Setting timer to pause debugger in 400ms...');
  setTimeout(async () => {
    console.log('SENDING Debugger.pause...');
    await cdp.send('Debugger.pause');
  }, 400);

  console.log('Releasing mouse up (this triggers the freeze)...');
  await page.mouse.up();
})().catch(err => {
  console.error(err);
  process.exit(1);
});
