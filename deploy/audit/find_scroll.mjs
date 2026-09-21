import { chromium } from 'playwright';
(async () => {
  const browser = await chromium.launch();
  for (const p of ['/', '/kirish']) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto('https://rung.shats.uz' + p, { waitUntil: 'networkidle' });
    const overflowing = await page.evaluate(() => {
      const bad = [];
      document.querySelectorAll('*').forEach(el => {
        if (el.scrollWidth > el.clientWidth + 1) bad.push(el.tagName + '.' + el.className);
      });
      return bad;
    });
    console.log('Overflowing on ' + p + ' at 390x844:', overflowing);
    await page.close();
  }
  await browser.close();
})();
