const { chromium } = require('@playwright/test');

(async () => {
  console.log('Connecting to browser...');
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  page.on('console', msg => console.log(`[PAGE LOG] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR]: ${err.message}\n${err.stack}`));
  page.on('crash', () => console.log('[PAGE CRASHED]!'));

  console.log('Navigating to http://localhost:5173/auth ...');
  await page.goto('http://localhost:5173/auth', { waitUntil: 'domcontentloaded' });
  console.log('Page loaded. URL:', page.url());

  console.log('Looking for email input...');
  const emailInput = page.locator('#email');
  await emailInput.waitFor({ state: 'visible', timeout: 5000 });
  console.log('Email input found. Clicking into it...');
  await emailInput.click();

  console.log('Starting to type into email input...');
  const testString = 'testuser@example.com';
  const startTime = Date.now();
  for (let i = 0; i < testString.length; i++) {
    const char = testString[i];
    const charStart = Date.now();
    await emailInput.press(char);
    const charDuration = Date.now() - charStart;
    console.log(`Typed '${char}' in ${charDuration}ms`);
  }
  const totalDuration = Date.now() - startTime;
  console.log(`Total typing time: ${totalDuration}ms for ${testString.length} chars`);

  const val = await emailInput.inputValue();
  console.log('Input value is now:', val);

  console.log('Now checking password input...');
  const passwordInput = page.locator('#password');
  await passwordInput.click();
  const pStart = Date.now();
  await passwordInput.fill('SecretPassword123!');
  console.log(`Password filled in ${Date.now() - pStart}ms`);

  await browser.close();
  console.log('Done!');
})().catch(err => {
  console.error('Script error:', err);
  process.exit(1);
});
