"""add public_id

Revision ID: 1ac49fab3453
Revises: 0002
Create Date: 2026-09-22 00:33:29.523354

"""
from __future__ import annotations
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1ac49fab3453'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('listings', sa.Column('public_id', sa.String(length=12), nullable=True))
    op.create_index(op.f('ix_listings_public_id'), 'listings', ['public_id'], unique=True)
    
    # Generate public IDs for existing rows
    import uuid
    from sqlalchemy.orm import Session
    from sqlalchemy.sql import table, column, select, update
    
    bind = op.get_bind()
    session = Session(bind=bind)
    
    listings = table('listings',
        column('id', sa.String()),
        column('public_id', sa.String())
    )
    
    for row in session.execute(select(listings.c.id)).fetchall():
        new_id = uuid.uuid4().hex[:12]
        session.execute(
            update(listings).where(listings.c.id == row.id).values(public_id=new_id)
        )
    session.commit()
    
    op.alter_column('listings', 'public_id', existing_type=sa.String(length=12), nullable=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_listings_public_id'), table_name='listings')
    op.drop_column('listings', 'public_id')
