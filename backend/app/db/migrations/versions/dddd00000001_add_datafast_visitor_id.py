"""add_datafast_visitor_id_to_topup_orders

Revision ID: dddd00000001
Revises: cccc00000001
Create Date: 2026-09-22 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'dddd00000001'
down_revision: Union[str, None] = 'cccc00000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('topup_orders', sa.Column('datafast_visitor_id', sa.String(length=256), nullable=True))


def downgrade() -> None:
    op.drop_column('topup_orders', 'datafast_visitor_id')
