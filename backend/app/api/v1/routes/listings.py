from __future__ import annotations
import logging
from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import get_db
from app.models.listing import Listing
from app.models.stats import ListingStatsDaily
from app.schemas.public import ListingDetail

router = APIRouter(prefix="/listings", tags=["listings"])
logger = logging.getLogger(__name__)


def _extract_clean_handle(raw_handle: str) -> str:
    h = (raw_handle or "").strip()
    for prefix in [
        "https://t.me/", "http://t.me/", "t.me/",
        "https://telegram.me/", "http://telegram.me/", "telegram.me/"
    ]:
        if h.lower().startswith(prefix):
            h = h[len(prefix):]
            break
    return h.lstrip("@").strip("/")


async def _sync_telegram_subscribers(listing: Listing, db: AsyncSession) -> bool:
    """Fetch subscriber count from Telegram Bot API and update listing if needed."""
    clean_handle = _extract_clean_handle(listing.handle)
    if not clean_handle:
        return False
        
    settings = get_settings()
    dirty = False
    proper_handle = f"@{clean_handle}"
    proper_url = f"https://t.me/{clean_handle}"
    
    if listing.handle != proper_handle:
        listing.handle = proper_handle
        dirty = True
    if not listing.url or listing.url != proper_url:
        listing.url = proper_url
        dirty = True
        
    if settings.BOT_TOKEN:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getChatMemberCount",
                    params={"chat_id": proper_handle}
                )
                if res.is_success:
                    data = res.json()
                    if data.get("ok"):
                        new_count = int(data.get("result", 0))
                        if new_count > 0 and listing.subscribers != new_count:
                            listing.subscribers = new_count
                            dirty = True
        except Exception as e:
            logger.warning("Failed to auto-sync Telegram subscribers for %s: %s", proper_handle, e)

    if not listing.logo_url and settings.BOT_TOKEN:
        from app.api.v1.routes.uploads import fetch_and_save_telegram_avatar
        try:
            fetched_logo = await fetch_and_save_telegram_avatar(proper_handle)
            if fetched_logo:
                listing.logo_url = fetched_logo
                dirty = True
        except Exception as e:
            logger.warning("Failed to auto-fetch Telegram logo for %s: %s", proper_handle, e)
            
    if dirty:
        await db.commit()
        await db.refresh(listing)
    return dirty


@router.get("/{identifier}", response_model=ListingDetail)
async def get_listing(
    identifier: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ListingDetail:
    """Get a single listing by id or handle."""
    try:
        listing_id = UUID(identifier)
        stmt = select(Listing).where(Listing.id == listing_id, Listing.deleted_at.is_(None))
    except ValueError:
        clean = _extract_clean_handle(identifier)
        handles_to_try = [identifier, f"@{clean}", clean]
        if identifier.startswith('_'):
            handles_to_try.append('@' + identifier[1:])
            handles_to_try.append('@' + identifier.strip('_'))
        stmt = select(Listing).where(Listing.handle.in_(handles_to_try), Listing.deleted_at.is_(None))
        
    result = await db.execute(
        stmt.options(selectinload(Listing.category))
    )
    listing = result.scalars().first()
    if listing is None or listing.status != "active":
        raise HTTPException(status_code=404, detail="Listing not found")

    # Auto-sync subscribers and normalize handle if subscribers == 0 or handle has URL
    if (listing.subscribers == 0 or listing.handle.startswith("http") or not listing.url or not listing.logo_url):
        await _sync_telegram_subscribers(listing, db)

    # Total clickthroughs
    clicks_result = await db.execute(
        select(func.sum(ListingStatsDaily.clickthroughs)).where(
            ListingStatsDaily.listing_id == listing.id
        )
    )
    clickthroughs = int(clicks_result.scalar_one() or 0)

    clean_h = _extract_clean_handle(listing.handle)
    return ListingDetail(
        id=listing.id,
        kind=listing.kind,
        handle=listing.handle,
        name=listing.name,
        description=listing.description,
        url=listing.url or f"https://t.me/{clean_h}",
        category_slug=listing.category.slug if listing.category else None,
        category_color=listing.category.color if listing.category else None,
        subscribers=listing.subscribers,
        verified=listing.verified,
        claimed=listing.claimed,
        free_label=listing.free_label,
        logo_url=listing.logo_url,
        gradient_start=listing.gradient_start,
        gradient_end=listing.gradient_end,
        clickthroughs=clickthroughs,
        created_at=listing.created_at,
        status=listing.status,
        bot_is_admin=listing.bot_is_admin,
    )


@router.post("/{identifier}/sync", response_model=ListingDetail)
async def sync_listing(
    identifier: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ListingDetail:
    """Force sync Telegram subscribers and metadata for a listing."""
    try:
        listing_id = UUID(identifier)
        stmt = select(Listing).where(Listing.id == listing_id, Listing.deleted_at.is_(None))
    except ValueError:
        clean = _extract_clean_handle(identifier)
        handles_to_try = [identifier, f"@{clean}", clean]
        stmt = select(Listing).where(Listing.handle.in_(handles_to_try), Listing.deleted_at.is_(None))

    result = await db.execute(stmt.options(selectinload(Listing.category)))
    listing = result.scalars().first()
    if listing is None or listing.status != "active":
        raise HTTPException(status_code=404, detail="Listing not found")

    await _sync_telegram_subscribers(listing, db)
    return await get_listing(str(listing.id), db)


@router.get("/{identifier}/subscriber-stats")
async def get_subscriber_stats(
    identifier: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get time-series data of subscriber joins and leaves."""
    try:
        listing_id = UUID(identifier)
        stmt = select(Listing).where(Listing.id == listing_id, Listing.deleted_at.is_(None))
    except ValueError:
        clean = _extract_clean_handle(identifier)
        handles_to_try = [identifier, f"@{clean}", clean]
        stmt = select(Listing).where(Listing.handle.in_(handles_to_try), Listing.deleted_at.is_(None))

    result = await db.execute(stmt)
    listing = result.scalars().first()
    if listing is None or listing.status != "active":
        raise HTTPException(status_code=404, detail="Listing not found")

    from app.models.subscriber_events import SubscriberEvent
    
    # Fetch events for the last 30 days
    # To keep it simple, we just return the raw events for now, or aggregate by day.
    # Grouping by day and action:
    # SELECT date_trunc('day', created_at) as day, action, count(*) 
    # FROM subscriber_events WHERE listing_id = ? GROUP BY 1, 2 ORDER BY 1
    
    stats_stmt = (
        select(
            func.date_trunc('day', SubscriberEvent.created_at).label('day'),
            SubscriberEvent.action,
            func.count(SubscriberEvent.id).label('count')
        )
        .where(SubscriberEvent.listing_id == listing.id)
        .group_by('day', SubscriberEvent.action)
        .order_by('day')
    )
    
    stats_result = await db.execute(stats_stmt)
    
    # Format into a list of { date: '2023-10-01', joins: 5, leaves: 2 }
    daily_stats = {}
    for row in stats_result:
        day_str = row.day.strftime('%Y-%m-%d') if row.day else "unknown"
        if day_str not in daily_stats:
            daily_stats[day_str] = {"date": day_str, "joins": 0, "leaves": 0}
            
        if row.action == "join":
            daily_stats[day_str]["joins"] = row.count
        elif row.action == "leave":
            daily_stats[day_str]["leaves"] = row.count
            
    return sorted(list(daily_stats.values()), key=lambda x: x["date"])

