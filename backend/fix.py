import re
import os

files = ['app/db/migrations/versions/0001_initial.py', 'app/db/migrations/versions/0002_s1_models.py']

for filename in files:
    filename = "/home/kai/projects/rung/backend/" + filename
    if not os.path.exists(filename):
        print(f"Not found: {filename}")
        continue
    with open(filename, 'r') as f:
        content = f.read()

    # Replace BigInteger with String(length=36) for IDs
    content = re.sub(r"sa\.Column\('id',\s*sa\.BigInteger\(\),\s*autoincrement=True", r"sa.Column('id', sa.String(length=36)", content)
    content = re.sub(r"sa\.Column\('id',\s*sa\.BigInteger\(\)", r"sa.Column('id', sa.String(length=36))", content)
    content = re.sub(r"sa\.Column\('category_id',\s*sa\.BigInteger\(\)", r"sa.Column('category_id', sa.String(length=36))", content)
    content = re.sub(r"sa\.Column\('user_id',\s*sa\.BigInteger\(\)", r"sa.Column('user_id', sa.String(length=36))", content)
    content = re.sub(r"sa\.Column\('listing_id',\s*sa\.BigInteger\(\)", r"sa.Column('listing_id', sa.String(length=36))", content)
    content = re.sub(r"sa\.Column\('board_id',\s*sa\.BigInteger\(\)", r"sa.Column('board_id', sa.String(length=36))", content)
    content = re.sub(r"sa\.Column\('deleted_by',\s*sa\.BigInteger\(\)", r"sa.Column('deleted_by', sa.String(length=36))", content)

    # In 0002_s1_models.py, listings table: change slug to public_id and length 128 to 12
    if '0002' in filename:
        content = content.replace("sa.Column('slug', sa.String(length=128)", "sa.Column('public_id', sa.String(length=12)")
        content = content.replace("op.create_index('ix_listings_slug', 'listings', ['slug'])", "op.create_index('ix_listings_public_id', 'listings', ['public_id'])")

    with open(filename, 'w') as f:
        f.write(content)
    print(f"Fixed {filename}")
