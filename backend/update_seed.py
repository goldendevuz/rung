import re
import uuid

path = '/home/kai/projects/rung/backend/app/db/seed.py'
with open(path) as f:
    c = f.read()

c = c.replace('public_id', 'id')

if 'uuid5' not in c:
    c = c.replace('from sqlalchemy import select', 'import uuid\nfrom sqlalchemy import select')

c = re.sub(r'"id":"s*"([^"]+)"', r'"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "\1"))', c)
c = re.sub(r'slug=c["\"slug\"],', r'id=uuid.uuid5(uuid.NAMESPACE_URL, c["slug"]), slug=c["slug"],', c)

with open(path, 'w') as f:
    f.write(c)
print('seed.py updated')