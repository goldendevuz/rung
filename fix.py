import re

path = '/home/kai/projects/rung/deploy/audit/audit.mjs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

good = 'if (hasScroll) failures.push(' + chr(96) + ' : horizontal scroll detected' + chr(96) + ');'
content = re.sub(
    r'if \(hasScroll\) failures\.push\(.*?: horizontal scroll detected\);',
    good,
    content
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed audit.mjs')
