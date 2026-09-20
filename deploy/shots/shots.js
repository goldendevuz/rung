const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch();

  const p1 = await browser.newPage();
  await p1.setViewportSize({ width: 1440, height: 900 });
  await p1.goto('http://localhost', { waitUntil: 'networkidle' });
  await p1.screenshot({ path: '/shots/desktop-1440x900.png', fullPage: false });
  console.log('desktop-1440x900.png saved');

  const p2 = await browser.newPage();
  await p2.setViewportSize({ width: 390, height: 844 });
  await p2.goto('http://localhost', { waitUntil: 'networkidle' });
  await p2.screenshot({ path: '/shots/mobile-390x844.png', fullPage: false });
  console.log('mobile-390x844.png saved');

  await browser.close();
  console.log('All screenshots done');
})();
