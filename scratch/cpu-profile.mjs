import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);

  page.on('console', msg => console.log(`[PAGE LOG] ${msg.type()}: ${msg.text()}`));
  page.on('pageerror', err => console.log(`[PAGE ERROR]: ${err.message}`));

  await page.goto('http://localhost:5173/auth', { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('#email');

  const rect = await page.evaluate(() => {
    const r = document.getElementById('email').getBoundingClientRect();
    return { x: r.x + 10, y: r.y + 10 };
  });

  await page.mouse.move(rect.x, rect.y);
  await page.mouse.down();

  await cdp.send('Profiler.enable');
  await cdp.send('Profiler.start');

  console.log('Profiling started. Setting timeout to stop profile and dump heavy nodes...');
  setTimeout(async () => {
    console.log('Stopping profiler...');
    const { profile } = await cdp.send('Profiler.stop');
    console.log(`Profile collected: ${profile.nodes.length} nodes, ${profile.samples?.length} samples`);

    // Count hit counts for each node
    const counts = {};
    for (const id of profile.samples || []) {
      counts[id] = (counts[id] || 0) + 1;
    }

    const sorted = Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 15);

    console.log('Top hot nodes:');
    for (const [id, count] of sorted) {
      const node = profile.nodes.find(n => n.id === Number(id));
      const call = node?.callFrame;
      console.log(`  Hits: ${count} - ${call?.functionName || '(anon)'} (${call?.url}:${call?.lineNumber})`);
    }
    await browser.close();
    process.exit(0);
  }, 1000);

  console.log('Now releasing mouse up...');
  await page.mouse.up();
})().catch(err => {
  console.error(err);
  process.exit(1);
});
