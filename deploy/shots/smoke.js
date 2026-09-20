const { chromium } = require('@playwright/test');

(async () => {
  let hasErrors = false;
  const browser = await chromium.launch();
  const routes = ['/', '/kunlik', '/kategoriyalar', '/qoshish', '/haqida', '/qoidalar', '/kirish'];

  for (const route of routes) {
    const page = await browser.newPage();
    const url = `http://localhost${route}`;
    console.log(`Checking ${url}...`);

    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error(`[CONSOLE ERROR on ${route}]: ${msg.text()}`);
        hasErrors = true;
      }
    });

    page.on('pageerror', err => {
      console.error(`[PAGE ERROR on ${route}]: ${err.message}`);
      hasErrors = true;
    });

    await page.goto(url, { waitUntil: 'networkidle' });

    // Check Vite error overlay
    const hasOverlay = await page.evaluate(() => {
      return !!document.querySelector('vite-error-overlay');
    });

    if (hasOverlay) {
      console.error(`[VITE ERROR OVERLAY on ${route}]`);
      hasErrors = true;
    }

    if (route === '/') {
      // Must have >= 14 ranked rows. Let's check rows with rank.
      const rowCount = await page.locator('.row').count();
      console.log(`Found ${rowCount} rows on /`);
      if (rowCount < 14) {
        console.error(`[ERROR on ${route}]: Expected >= 14 rows, found ${rowCount}`);
        hasErrors = true;
      }
    }

    await page.close();
  }

  await browser.close();

  if (hasErrors) {
    console.error('Smoke test FAILED.');
    process.exit(1);
  } else {
    console.log('Smoke test PASSED.');
  }
})();
