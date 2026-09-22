"""add_topup_and_ledger_tables

Revision ID: bbbb00000001
Revises: aaaa00000001
Create Date: 2026-09-22 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bbbb00000001'
down_revision: Union[str, None] = 'aaaa00000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. topup_orders
    op.create_table(
        'topup_orders',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('order_id', sa.String(length=128), nullable=False),
        sa.Column('b_amount', sa.BigInteger(), nullable=False),
        sa.Column('amount_uzs', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='pending', nullable=False),
        sa.Column('transaction_id', sa.String(length=128), nullable=True),
        sa.Column('pay_url', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_topup_orders_order_id'), 'topup_orders', ['order_id'], unique=True)
    op.create_index(op.f('ix_topup_orders_user_id'), 'topup_orders', ['user_id'], unique=False)
    op.create_index(op.f('ix_topup_orders_status'), 'topup_orders', ['status'], unique=False)

    # 2. ledger_entries
    op.create_table(
        'ledger_entries',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('delta_units', sa.BigInteger(), nullable=False),
        sa.Column('kind', sa.String(length=64), nullable=False),
        sa.Column('ref_type', sa.String(length=64), nullable=False),
        sa.Column('ref_id', sa.String(length=128), nullable=False),
        sa.Column('balance_after', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ref_id', name='uq_ledger_entries_ref_id')
    )
    op.create_index(op.f('ix_ledger_entries_user_id'), 'ledger_entries', ['user_id'], unique=False)
    op.create_index(op.f('ix_ledger_entries_ref_id'), 'ledger_entries', ['ref_id'], unique=True)


def downgrade() -> None:
    op.drop_table('ledger_entries')
    op.drop_table('topup_orders')
