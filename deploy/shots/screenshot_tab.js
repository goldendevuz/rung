const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 800, height: 400 } });
  
  // Wait for the dev server to be ready and load the mock tab
  await page.goto('file://' + path.resolve(__dirname, 'mock_tab.html'));
  await page.waitForTimeout(1000); // give it time to load the SVG favicon from localhost
  
  await page.screenshot({ path: '/shots/browser_tab.png' });
  await browser.close();
})();
