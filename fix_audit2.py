import sys

path = '/home/kai/projects/rung/deploy/audit/audit.mjs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''    rows.push({ mode, route: r.path, status: resp.status(), chars: text.length, errors: errs });
    if (resp.status() >= 400) failures.push(${mode} : HTTP );
    if (text.length < r.min) failures.push(${mode} : only  chars (min ));
    const hasScroll = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
    if (hasScroll) failures.push( : horizontal scroll detected);
    if (errs.length) failures.push(${mode} :  console/API errors: );'''

replacement = '''    const hasScroll = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
    rows.push({ mode, route: r.path, status: resp.status(), chars: text.length, errors: errs, hasScroll });
    if (resp.status() >= 400) failures.push(\\ \\: HTTP \\);
    if (text.length < r.min) failures.push(\\ \\: only \\ chars (min \\));
    if (hasScroll) failures.push(\\ \\: horizontal scroll detected);
    if (errs.length) failures.push(\\ \\: \\ console/API errors: \\);'''
# Fix backslash escaping for Python string literals
replacement = replacement.replace('\\\\', '\\')

if target in content:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.replace(target, replacement))
    print('Patched successfully!')
else:
    print('Target not found!')
    sys.exit(1)
