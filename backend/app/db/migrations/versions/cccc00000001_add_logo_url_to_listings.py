"""add_logo_url_to_listings

Revision ID: cccc00000001
Revises: bbbb00000001
Create Date: 2026-09-22 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'cccc00000001'
down_revision: Union[str, None] = 'bbbb00000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('listings', sa.Column('logo_url', sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column('listings', 'logo_url')
