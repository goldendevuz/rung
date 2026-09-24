"""add_balance_to_users

Revision ID: aaaa00000001
Revises: f0e19bec7e68
Create Date: 2026-09-22 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'aaaa00000001'
down_revision: Union[str, None] = 'f0e19bec7e68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('balance', sa.BigInteger(), nullable=False, server_default='0'))

def downgrade() -> None:
    op.drop_column('users', 'balance')
