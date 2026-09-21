const { chromium } = require('playwright');
const { execSync } = require('child_process');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(2000);
  
  // Take screenshot of the entire X11 display
  try {
    execSync('scrot /shots/tab.png || import -window root /shots/tab.png', { stdio: 'inherit' });
  } catch(e) {
    console.error("Screenshot command failed", e);
  }

  await browser.close();
})();
