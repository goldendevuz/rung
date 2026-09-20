"""Public stats endpoint."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.models.board import BoardEntry
from app.models.listing import Listing
from app.schemas.public import PublicStatsOut

router = APIRouter(prefix="/stats", tags=["stats"])
settings = get_settings()


@router.get("/public", response_model=PublicStatsOut)
async def get_public_stats(db: Annotated[AsyncSession, Depends(get_db)]) -> PublicStatsOut:
    """Real counts only. Online/visits hidden behind SHOW_LIVE_STATS flag."""
    total_listings = (
        await db.execute(
            select(func.count(Listing.id)).where(
                Listing.status == "active", Listing.deleted_at.is_(None)
            )
        )
    ).scalar_one() or 0

    total_entries = (
        await db.execute(
            select(func.count(BoardEntry.id)).where(
                BoardEntry.status == "active", BoardEntry.deleted_at.is_(None)
            )
        )
    ).scalar_one() or 0

    show_live = getattr(settings, "SHOW_LIVE_STATS", False)

    return PublicStatsOut(
        total_listings=total_listings,
        total_entries=total_entries,
        online_now=None if not show_live else 0,
        visits_today=None if not show_live else 0,
    )
