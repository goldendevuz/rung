"""Initial empty migration.

Revision ID: 0001
Revises:
Create Date: 2026-09-20

"""
from __future__ import annotations
from typing import Sequence, Union

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # S0: empty first revision — actual tables added in S1
    pass


def downgrade() -> None:
    pass
