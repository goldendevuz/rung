"""Click tracking and redirect endpoint."""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.periods import now_tashkent
from app.core.redis import get_redis
from app.core.rate_limit import rate_limit
from app.db.session import get_db
from app.models.listing import Listing
from app.models.stats import ListingStatsDaily

router = APIRouter(tags=["clicks"])


@router.api_route(
    "/go/{listing_id}",
    methods=["GET", "HEAD"],
    dependencies=[Depends(rate_limit("go_redirect", limit=30, window_seconds=60))]
)
async def redirect_to_listing(
    listing_id: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Track click-through and redirect to external channel URL."""
    try:
        lid = uuid.UUID(listing_id)
        query = select(Listing).where(Listing.id == lid, Listing.deleted_at.is_(None))
    except ValueError:
        clean_slug = listing_id.lstrip("@").lower()
        query = select(Listing).where(Listing.handle.ilike(f"%{clean_slug}%"), Listing.deleted_at.is_(None))

    result = await db.execute(query)
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Kanal topilmadi")

    # Record click atomically in database
    today = now_tashkent().date()
    try:
        stmt = (
            insert(ListingStatsDaily)
            .values(listing_id=listing.id, stat_date=today, clickthroughs=1)
            .on_conflict_do_update(
                index_elements=["listing_id", "stat_date"],
                set_={"clickthroughs": ListingStatsDaily.clickthroughs + 1},
            )
        )
        await db.execute(stmt)
        await db.commit()
    except Exception:
        await db.rollback()

    # Also increment in Redis cache
    redis = await get_redis()
    if redis:
        try:
            await redis.hincrby("stats:listing_clicks", str(listing.id), 1)
        except Exception:
            pass

    # Target URL
    target_url = listing.url
    if not target_url or not target_url.startswith("http"):
        handle_clean = listing.handle.lstrip("@")
        target_url = f"https://t.me/{handle_clean}"

    return RedirectResponse(url=target_url, status_code=302)
