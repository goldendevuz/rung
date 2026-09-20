"""S1 models: categories, listings, boards, board_entries, listing_stats_daily, settings.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-20

"""
from __future__ import annotations
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── categories ────────────────────────────────────────────────────────────
    op.create_table(
        'categories',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('slug', sa.String(length=64), nullable=False),
        sa.Column('name_uz', sa.String(length=80), nullable=False),
        sa.Column('color', sa.String(length=32), nullable=False),
        sa.Column('icon', sa.String(length=8), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.BigInteger(), nullable=True),
        sa.Column('delete_reason', sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('slug'),
    )
    op.create_index('ix_categories_slug', 'categories', ['slug'])

    # ── listings ──────────────────────────────────────────────────────────────
    op.create_table(
        'listings',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('slug', sa.String(length=128), nullable=False),
        sa.Column('kind', sa.String(length=32), nullable=False),
        sa.Column('handle', sa.String(length=128), nullable=False),
        sa.Column('name', sa.String(length=60), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url', sa.String(length=512), nullable=True),
        sa.Column('category_id', sa.BigInteger(), nullable=True),
        sa.Column('subscribers', sa.BigInteger(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=False),
        sa.Column('claimed', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('free_label', sa.String(length=128), nullable=True),
        sa.Column('gradient_start', sa.String(length=32), nullable=False),
        sa.Column('gradient_end', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.BigInteger(), nullable=True),
        sa.Column('delete_reason', sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('slug'),
    )
    op.create_index('ix_listings_slug', 'listings', ['slug'])
    op.create_index('ix_listings_category_id', 'listings', ['category_id'])
    op.create_index('ix_listings_status', 'listings', ['status'])

    # ── boards ────────────────────────────────────────────────────────────────
    op.create_table(
        'boards',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('period_type', sa.String(length=32), nullable=False),
        sa.Column('period_key', sa.String(length=32), nullable=False),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('period_type', 'period_key', name='uq_board_period'),
    )
    op.create_index('ix_boards_period_type', 'boards', ['period_type'])
    op.create_index('ix_boards_status', 'boards', ['status'])

    # ── board_entries ─────────────────────────────────────────────────────────
    op.create_table(
        'board_entries',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('board_id', sa.BigInteger(), nullable=False),
        sa.Column('listing_id', sa.BigInteger(), nullable=False),
        sa.Column('paid_units', sa.BigInteger(), nullable=False),
        sa.Column('entered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.BigInteger(), nullable=True),
        sa.Column('delete_reason', sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
    )
    op.create_index('ix_board_entries_board_id', 'board_entries', ['board_id'])
    op.create_index('ix_board_entries_listing_id', 'board_entries', ['listing_id'])
    op.create_index('ix_board_entries_status', 'board_entries', ['status'])
    # Partial unique index: one active entry per listing per board
    op.create_index(
        'ix_board_entries_active_listing',
        'board_entries',
        ['board_id', 'listing_id'],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )
    # Fast rank derivation
    op.create_index(
        'ix_board_entries_rank',
        'board_entries',
        ['board_id', 'paid_units', 'entered_at'],
        postgresql_where=sa.text("status = 'active'"),
    )

    # ── listing_stats_daily ───────────────────────────────────────────────────
    op.create_table(
        'listing_stats_daily',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('listing_id', sa.BigInteger(), nullable=False),
        sa.Column('stat_date', sa.Date(), nullable=False),
        sa.Column('clickthroughs', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('listing_id', 'stat_date', name='uq_stats_listing_date'),
    )
    op.create_index('ix_listing_stats_daily_listing_id', 'listing_stats_daily', ['listing_id'])

    # ── settings ──────────────────────────────────────────────────────────────
    op.create_table(
        'settings',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('key'),
    )
    op.create_index('ix_settings_key', 'settings', ['key'])


def downgrade() -> None:
    op.drop_table('settings')
    op.drop_table('listing_stats_daily')
    op.drop_table('board_entries')
    op.drop_table('boards')
    op.drop_table('listings')
    op.drop_table('categories')
