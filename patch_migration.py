import re

file_path = '/home/kai/projects/rung/backend/app/db/migrations/versions/451003a41085_use_public_id.py'

with open(file_path, 'r') as f:
    content = f.read()

new_content = content.replace(", nullable=False))", ", nullable=True))")

tables = ['board_entries', 'boards', 'categories', 'listing_stats_daily', 'settings', 'users']

for table in tables:
    target = f"op.add_column('{table}', sa.Column('public_id', sa.String(length=12), nullable=True))"
    replacement = f"""op.add_column('{table}', sa.Column('public_id', sa.String(length=12), nullable=True))
    op.execute("UPDATE {table} SET public_id = substr(md5(random()::text), 1, 12) WHERE public_id IS NULL")
    op.alter_column('{table}', 'public_id', nullable=False)"""
    new_content = new_content.replace(target, replacement)

with open(file_path, 'w') as f:
    f.write(new_content)
