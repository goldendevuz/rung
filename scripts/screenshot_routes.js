const { chromium } = require('@playwright/test');

const routes = [
  { path: '/', name: 'home' },
  { path: '/kunlik', name: 'kunlik' },
  { path: '/kategoriyalar', name: 'kategoriyalar' },
  { path: '/qoshish', name: 'qoshish' },
  { path: '/haqida', name: 'haqida' },
  { path: '/qoidalar', name: 'qoidalar' },
  { path: '/kirish', name: 'kirish' },
  { path: '/p/non-existing-slug', name: 'listing-404' },
  { path: '/404-test-page', name: '404' }
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  
  // Normal mode
  const contextNormal = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const pageNormal = await contextNormal.newPage();
  for (const r of routes) {
    console.log(`Navigating to https://rung.shats.uz${r.path} (normal)`);
    await pageNormal.goto(`https://rung.shats.uz${r.path}`, { waitUntil: 'networkidle' });
    await pageNormal.waitForTimeout(1000);
    await pageNormal.screenshot({ path: `/shots/${r.name}.png` });
  }
  await contextNormal.close();

  // Demo mode
  const contextDemo = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const pageDemo = await contextDemo.newPage();
  
  await pageDemo.goto('https://rung.shats.uz/');
  await pageDemo.evaluate(() => localStorage.setItem('rung_demo', '1'));

  for (const r of routes) {
    console.log(`Navigating to https://rung.shats.uz${r.path} (demo)`);
    await pageDemo.goto(`https://rung.shats.uz${r.path}`, { waitUntil: 'networkidle' });
    await pageDemo.waitForTimeout(1000);
    await pageDemo.screenshot({ path: `/shots/${r.name}-demo.png` });
  }
  await contextDemo.close();
  await browser.close();
  console.log("Screenshots completed.");
})();
