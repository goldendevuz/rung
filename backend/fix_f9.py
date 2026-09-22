import re
import os

path = "/home/kai/projects/rung/backend/app/db/migrations/versions/f9180753eccb_s2_auth_public_id.py"

with open(path, "r") as f:
    code = f.read()

code = code.replace("from typing import Sequence, Union", "from typing import Sequence, Union\nimport random\nimport string")

backfill = """
    # Make nullable=True first
    op.add_column('listings', sa.Column('public_id', sa.String(length=12), nullable=True))
    
    # Backfill existing rows with random 10-char strings (base62 style)
    connection = op.get_bind()
    listings = connection.execute(sa.text("SELECT id FROM listings")).fetchall()
    
    # Base62 alphabet
    chars = string.ascii_letters + string.digits
    for row in listings:
        pub_id = "".join(random.choice(chars) for _ in range(10))
        connection.execute(
            sa.text("UPDATE listings SET public_id = :pub_id WHERE id = :id"),
            {"pub_id": pub_id, "id": row[0]}
        )
    
    # Now set nullable=False
    op.alter_column('listings', 'public_id', nullable=False)
"""

code = code.replace(
    "op.add_column('listings', sa.Column('public_id', sa.String(length=12), nullable=False))",
    backfill.strip()
)

with open(path, "w") as f:
    f.write(code)
