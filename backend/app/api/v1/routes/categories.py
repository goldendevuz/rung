"""Categories API endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.board import Board, BoardEntry
from app.models.category import Category
from app.models.listing import Listing
from app.schemas.public import CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
async def list_categories(db: Annotated[AsyncSession, Depends(get_db)]) -> list[CategoryOut]:
    """All categories with active listing counts."""
    result = await db.execute(
        select(Category)
        .where(Category.deleted_at.is_(None))
        .order_by(Category.sort_order)
    )
    cats = list(result.scalars())

    # Count active listings per category
    count_result = await db.execute(
        select(Listing.category_id, func.count(Listing.id).label("cnt"))
        .where(Listing.status == "active", Listing.deleted_at.is_(None))
        .group_by(Listing.category_id)
    )
    counts: dict[int, int] = {row.category_id: row.cnt for row in count_result}

    # Compute next rank price per category from all_time board
    rank1_result = await db.execute(
        select(Listing.category_id, func.max(BoardEntry.paid_units).label("max_paid"))
        .join(BoardEntry, BoardEntry.listing_id == Listing.id)
        .join(Board, Board.id == BoardEntry.board_id)
        .where(
            BoardEntry.status == "active",
            BoardEntry.deleted_at.is_(None),
            Board.period_type == "all_time",
            Board.status == "active",
        )
        .group_by(Listing.category_id)
    )
    rank1_prices: dict[int, int] = {row.category_id: int(row.max_paid or 0) for row in rank1_result}

    return [
        CategoryOut(
            slug=c.slug,
            name_uz=c.name_uz,
            color=c.color,
            icon=c.icon,
            listing_count=counts.get(c.id, 0),
            next_rank_price_b=(rank1_prices.get(c.id, 0) // 1000) + 1,
        )
        for c in cats
    ]
