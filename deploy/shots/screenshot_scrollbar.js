const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto('http://localhost/', { waitUntil: 'networkidle' });
  
  // Ensure enough content to scroll and then scroll down
  await page.evaluate(() => {
    const div = document.createElement('div');
    div.style.height = '1000px';
    document.body.appendChild(div);
    window.scrollBy(0, 300);
  });
  
  await page.waitForTimeout(1000); // give scrollbar time to render if it fades, though custom shouldn't fade
  
  await page.screenshot({ path: '/shots/desktop-dark-scrolled.png', fullPage: false });
  console.log('Saved dark mode screenshot');
  
  // Click theme toggle button
  await page.click('button[aria-label="Mavzuni almashtirish"]');
  await page.waitForTimeout(1000);
  
  await page.screenshot({ path: '/shots/desktop-light-scrolled.png', fullPage: false });
  console.log('Saved light mode screenshot');
  
  await browser.close();
})();
