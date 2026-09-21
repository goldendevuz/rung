import { chromium } from 'playwright';
import fs from 'node:fs';

// Usage: BASE=https://rung.shats.uz EXPECT_DEMO=true node audit.mjs
// Exits with code 1 if any check fails.
const BASE = process.env.BASE || 'https://rung.shats.uz';
const EXPECT_DEMO = process.env.EXPECT_DEMO !== 'false';
fs.mkdirSync('shots', { recursive: true });

const routes = [
  { path: '/', min: 400 },
  { path: '/kunlik', min: 200 },
  { path: '/kategoriyalar', min: 200 },
  { path: '/qoshish', min: 700 },
  { path: '/haqida', min: 500 },
  { path: '/qoidalar', min: 1000 },
  { path: '/kirish', min: 500 },
  { path: '/login', min: 500 },
  // an unknown listing: the API answers 404 on purpose, the page must show a friendly message
  { path: '/p/yoq-bunday-kanal', min: 150, ignore: /listings|Failed to load resource/ },
  // an unknown client route: the app must render its own 404 page
  { path: '/mavjud-emas', min: 150 },
];
let demoOnly = [];
try {
  const res = await fetch(`${BASE}/api/v1/categories/1/listings`);
  const data = await res.json();
  if (data.items && data.items.length > 0) {
    demoOnly.push({ path: `/p/${data.items[0].public_id}`, min: 500 });
  } else {
    demoOnly.push({ path: '/p/_kodlash_uz_', min: 500 });
  }
} catch (e) {
  demoOnly.push({ path: '/p/_kodlash_uz_', min: 500 });
}

const failures = [];
const rows = [];

async function walk(mode, page, list, errors) {
  for (const r of list) {
    errors.length = 0;
    const resp = await page.goto(BASE + r.path, { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);
    const text = (await page.locator('body').innerText()).replace(/\s+/g, ' ').trim();
    const shot = 'shots/' + mode + (r.path === '/' ? '_home' : r.path.replace(/\//g, '_')) + '.png';
    await page.screenshot({ path: shot, fullPage: true });
    const errs = errors.filter((e) => !(r.ignore && r.ignore.test(e)));
    const hasScroll = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
    rows.push({ mode, route: r.path, status: resp.status(), chars: text.length, errors: errs, hasScroll });
    if (resp.status() >= 400) failures.push(`${mode} ${r.path}: HTTP ${resp.status()}`);
    if (text.length < r.min) failures.push(`${mode} ${r.path}: only ${text.length} chars (min ${r.min})`);
    if (hasScroll) failures.push(`${mode} ${r.path}: horizontal scroll detected`);
    if (errs.length) failures.push(`${mode} ${r.path}: ${errs.length} console/API errors: ${errs.join(' | ')}`);
  }
}

const browser = await chromium.launch();
for (const mode of ['normal', 'demo']) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text().slice(0, 120)); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message.slice(0, 120)));
  page.on('response', (r) => { if (r.status() >= 400) errors.push(r.status() + ' ' + r.url().replace(BASE, '')); });

  if (mode === 'demo') {
    await page.goto(BASE + '/', { waitUntil: 'networkidle' });
    const btn = page.getByRole('button', { name: /demo/i }).first();
    if (!(await btn.count())) {
      if (EXPECT_DEMO) failures.push('demo: the Demo button was not found');
      await ctx.close();
      continue;
    }
    await btn.click();
    await page.waitForTimeout(1500);
    const banner = await page.getByText(/Demo ma/i).count();
    if (!banner) failures.push('demo: banner "Demo ma\'lumotlar" is not visible after enabling demo mode');
    await walk(mode, page, [...routes, ...demoOnly], errors);
  } else {
    await walk(mode, page, routes, errors);
  }
  await ctx.close();
}
await browser.close();

for (const r of rows) console.log(JSON.stringify(r));
if (failures.length) {
  console.log('\nAUDIT FAILED:');
  for (const f of failures) console.log(' - ' + f);
  process.exit(1);
}
console.log('\nAUDIT PASSED');
