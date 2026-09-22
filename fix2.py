path = '/home/kai/projects/rung/deploy/audit/audit.mjs'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

start = c.find('async function walk')
end = c.find('const browser = await chromium.launch();')

walk_func = '''async function walk(mode, page, list, errors) {
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
    if (resp.status() >= 400) failures.push(''' + ' : HTTP ' + ''');
    if (text.length < r.min) failures.push(''' + ' : only  chars (min )' + ''');
    if (hasScroll) failures.push(''' + ' : horizontal scroll detected' + ''');
    if (errs.length) failures.push(''' + ' :  console/API errors: ' + ''');
  }
}

'''

walk_func = walk_func.replace('\\\\', '\\')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c[:start] + walk_func + c[end:])
print('Patched successfully!')
