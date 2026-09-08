import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('console', msg => console.log(`[PAGE LOG] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR]: ${err.message}`));

  await page.goto('http://localhost:5173/auth', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#email');

  console.log('Attaching diagnostics in browser context...');
  await page.evaluate(() => {
    let renderCount = 0;
    const observer = new MutationObserver((mutations) => {
      console.log(`[MUTATION] ${mutations.length} mutations. Target:`, mutations[0].target.nodeName);
    });
    observer.observe(document.body, { childList: true, subtree: true, attributes: true });

    const el = document.getElementById('email');
    el.addEventListener('input', (e) => console.log('[EVENT input] value:', e.target.value));
    el.addEventListener('change', (e) => console.log('[EVENT change] value:', e.target.value));
    el.addEventListener('keydown', (e) => console.log('[EVENT keydown] key:', e.key));
    el.addEventListener('focus', () => console.log('[EVENT focus]'));
  });

  console.log('Dispatching focus directly via DOM...');
  await page.evaluate(() => {
    const el = document.getElementById('email');
    el.focus();
  });

  console.log('Dispatching a single key event or value change directly...');
  const result = await page.evaluate(() => {
    const el = document.getElementById('email');
    const start = performance.now();
    el.value = 'a';
    el.dispatchEvent(new Event('input', { bubbles: true }));
    const dur = performance.now() - start;
    return { dur, val: el.value, connected: el.isConnected };
  });
  console.log('Evaluate result:', result);

  console.log('Checking if element is still connected after React re-render:');
  const check = await page.evaluate(() => {
    const el = document.getElementById('email');
    return {
      found: !!el,
      value: el?.value,
      parent: el?.parentElement?.className
    };
  });
  console.log('Check after render:', check);

  await browser.close();
  console.log('Done!');
})().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});
