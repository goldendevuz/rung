"""Public stats endpoint."""
from __future__ import annotations

import time
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.periods import now_tashkent
from app.core.redis import get_redis
from app.db.session import get_db
from app.models.board import BoardEntry
from app.models.listing import Listing
from app.schemas.public import PublicStatsOut

router = APIRouter(prefix="/stats", tags=["stats"])
settings = get_settings()


@router.get("/public", response_model=PublicStatsOut)
async def get_public_stats(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PublicStatsOut:
    """Return platform public stats with live active visitors & visits today."""
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

    total_paid_units = (
        await db.execute(
            select(func.sum(BoardEntry.paid_units)).where(
                BoardEntry.status == "active", BoardEntry.deleted_at.is_(None)
            )
        )
    ).scalar_one() or 0

    # Live online and visits tracking
    now_ts = int(time.time())
    today_str = now_tashkent().strftime("%Y-%m-%d")
    client_ip = request.client.host if request.client else "127.0.0.1"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    ua = request.headers.get("user-agent", "")
    visitor_hash = f"{client_ip}:{ua[:50]}"

    online_now = 1
    visits_today = 1

    redis = await get_redis()
    if redis:
        try:
            # Active in last 5 minutes (300 seconds)
            await redis.zadd("stats:active_visitors", {visitor_hash: now_ts})
            await redis.zremrangebyscore("stats:active_visitors", 0, now_ts - 300)
            active_count = await redis.zcard("stats:active_visitors")
            online_now = max(1, active_count)

            # Daily visits counter
            visits_key = f"stats:visits:{today_str}"
            visits_today = await redis.incr(visits_key)
            await redis.expire(visits_key, 86400 * 3)
        except Exception:
            pass

    return PublicStatsOut(
        total_listings=total_listings,
        total_entries=total_entries,
        online_now=online_now,
        visits_today=visits_today,
        total_paid_units=int(total_paid_units),
    )
