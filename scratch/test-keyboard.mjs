import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('console', msg => console.log(`[PAGE LOG] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR]: ${err.message}`));

  await page.goto('http://localhost:5173/auth', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#email');

  console.log('1. Click #email:');
  await page.click('#email');

  console.log('2. Check activeElement and DOM state:');
  const active = await page.evaluate(() => ({
    activeId: document.activeElement?.id,
    activeTag: document.activeElement?.tagName,
    emailExists: !!document.getElementById('email'),
    url: window.location.href
  }));
  console.log('Active element info:', active);

  console.log('3. Type using page.keyboard.type:');
  for (const ch of 'hello') {
    const t0 = Date.now();
    await page.keyboard.type(ch);
    console.log(`Typed '${ch}' in ${Date.now() - t0}ms, value:`, await page.evaluate(() => document.getElementById('email')?.value));
  }

  await browser.close();
  console.log('Finished without issues!');
})().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});
