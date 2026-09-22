import re

path = '/home/kai/projects/rung/deploy/audit/audit.mjs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = re.sub(
    r'(if \(text\.length < r\.min\) [^\n]+\n)',
    r'\1    const hasScroll = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);\n    if (hasScroll) failures.push(${mode} : horizontal scroll detected);\n',
    content
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('audit.mjs updated.')
