const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch();
  const routes = ['/', '/kunlik', '/kategoriyalar', '/qoshish'];

  for (const route of routes) {
    const p1 = await browser.newPage();
    await p1.setViewportSize({ width: 1440, height: 900 });
    await p1.goto(`http://localhost${route}`, { waitUntil: 'networkidle' });
    const nameDesktop = route === '/' ? 'home' : route.substring(1);
    await p1.screenshot({ path: `/shots/desktop-1440x900-${nameDesktop}.png`, fullPage: false });
    console.log(`desktop-1440x900-${nameDesktop}.png saved`);
    await p1.close();

    const p2 = await browser.newPage();
    await p2.setViewportSize({ width: 390, height: 844 });
    await p2.goto(`http://localhost${route}`, { waitUntil: 'networkidle' });
    const nameMobile = route === '/' ? 'home' : route.substring(1);
    await p2.screenshot({ path: `/shots/mobile-390x844-${nameMobile}.png`, fullPage: false });
    console.log(`mobile-390x844-${nameMobile}.png saved`);
    await p2.close();
  }

  await browser.close();
  console.log('All screenshots done');
})();
