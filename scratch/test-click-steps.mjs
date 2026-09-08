import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('console', msg => console.log(`[PAGE LOG] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR]: ${err.message}`));

  await page.goto('http://localhost:5173/auth', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#email');

  console.log('Inspecting event listeners...');
  const listeners = await page.evaluate(() => {
    const el = document.getElementById('email');
    const rect = el.getBoundingClientRect();
    return {
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
      outerHtml: el.outerHTML
    };
  });
  console.log('Element info:', listeners);

  console.log('Step 1: Moving mouse to element coords...');
  const t0 = Date.now();
  await page.mouse.move(listeners.rect.x + 10, listeners.rect.y + 10);
  console.log(`Mouse moved in ${Date.now() - t0}ms`);

  console.log('Step 2: Mouse down...');
  const t1 = Date.now();
  await page.mouse.down();
  console.log(`Mouse down in ${Date.now() - t1}ms`);

  console.log('Step 3: Mouse up...');
  const t2 = Date.now();
  await page.mouse.up();
  console.log(`Mouse up in ${Date.now() - t2}ms`);

  console.log('Step 4: Focus input...');
  const t3 = Date.now();
  await page.focus('#email');
  console.log(`Focused in ${Date.now() - t3}ms`);

  console.log('Step 5: Type single character with keyboard...');
  const t4 = Date.now();
  await page.keyboard.press('a');
  console.log(`Keyboard pressed in ${Date.now() - t4}ms`);

  await browser.close();
  console.log('All steps completed!');
})().catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});
