import json
import logging
import time
from datetime import timedelta
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.periods import now_tashkent
from app.core.redis import get_redis
from app.db.session import get_db
from app.models.board import BoardEntry
from app.models.listing import Listing
from app.schemas.public import PublicStatsOut, VisitorsStatsOut

logger = logging.getLogger(__name__)
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
            select(func.sum(BoardEntry.paid_units))
            .join(BoardEntry.listing)
            .where(
                BoardEntry.status == "active",
                BoardEntry.deleted_at.is_(None),
                func.lower(Listing.handle).notin_(["@rung_uz", "rung_uz", "@sipagentbot", "sipagentbot"]),
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

    highest_price = (
        await db.execute(
            select(func.max(BoardEntry.paid_units))
            .where(
                BoardEntry.status == "active",
                BoardEntry.deleted_at.is_(None),
            )
        )
    ).scalar_one() or 0

    return PublicStatsOut(
        total_listings=total_listings,
        total_entries=total_entries,
        online_now=online_now,
        visits_today=visits_today,
        total_paid_units=int(total_paid_units),
        highest_price=int(highest_price),
    )


def _extract_visitors(payload: dict) -> int:
    """Safely extract visitor count from DataFast analytics JSON payload."""
    if "visitors" in payload and isinstance(payload["visitors"], (int, float)):
        return int(payload["visitors"])
    data_field = payload.get("data")
    if isinstance(data_field, list) and len(data_field) > 0 and isinstance(data_field[0], dict):
        return int(data_field[0].get("visitors", 0) or 0)
    if isinstance(data_field, dict):
        return int(data_field.get("visitors", 0) or 0)
    return 0


@router.get("/visitors", response_model=VisitorsStatsOut)
async def get_visitors_stats() -> VisitorsStatsOut:
    """Return DataFast unique visitor stats with 60s Redis caching."""
    settings = get_settings()
    api_key = settings.DATAFAST_API_KEY
    if not api_key:
        return VisitorsStatsOut(
            configured=False,
            visitors_today=None,
            visitors_30d=None,
        )

    now = now_tashkent()
    today_str = now.strftime("%Y-%m-%d")
    start_30d = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    cache_key = f"datafast:visitors_overview:{today_str}"
    redis = await get_redis()
    if redis:
        try:
            cached = await redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return VisitorsStatsOut(**data)
        except Exception:
            pass

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            headers = {"Authorization": f"Bearer {api_key}"}

            resp_30d = await client.get(
                f"https://datafa.st/api/v1/analytics/overview?startAt={start_30d}&endAt={today_str}",
                headers=headers,
            )
            v_30d = 0
            if resp_30d.status_code == 200:
                v_30d = _extract_visitors(resp_30d.json())

            resp_today = await client.get(
                f"https://datafa.st/api/v1/analytics/overview?startAt={today_str}&endAt={today_str}",
                headers=headers,
            )
            v_today = 0
            if resp_today.status_code == 200:
                v_today = _extract_visitors(resp_today.json())

            result = VisitorsStatsOut(
                configured=True,
                visitors_today=v_today or 0,
                visitors_30d=v_30d or 0,
                start_at=start_30d,
                end_at=today_str,
            )

            if redis:
                try:
                    await redis.setex(cache_key, 60, json.dumps(result.model_dump()))
                except Exception:
                    pass

            return result
    except Exception as exc:
        logger.warning("DataFast analytics call failed: %s", exc)
        return VisitorsStatsOut(
            configured=True,
            visitors_today=0,
            visitors_30d=0,
            start_at=start_30d,
            end_at=today_str,
        )



from app.schemas.public import TimeseriesOut, TimeseriesDataPoint, TopClickedListingOut
from sqlalchemy.orm import selectinload

@router.get("/timeseries", response_model=TimeseriesOut)
async def get_timeseries_stats() -> TimeseriesOut:
    settings = get_settings()
    api_key = settings.DATAFAST_API_KEY
    if not api_key:
        return TimeseriesOut(configured=False, data=[])

    now = now_tashkent()
    start_time = (now - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
    end_time = now.strftime("%Y-%m-%dT%H:%M:%S")

    cache_key = f"datafast:timeseries_24h"
    redis = await get_redis()
    if redis:
        try:
            cached = await redis.get(cache_key)
            if cached:
                return TimeseriesOut(**json.loads(cached))
        except Exception:
            pass

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            headers = {"Authorization": f"Bearer {api_key}"}
            url = f"https://datafa.st/api/v1/analytics/timeseries?fields=pageviews&interval=hour&startAt={start_time}&endAt={end_time}"
            resp = await client.get(url, headers=headers)
            
            data_points = []
            if resp.status_code == 200:
                payload = resp.json()
                if "data" in payload and isinstance(payload["data"], list):
                    for item in payload["data"]:
                        if "date" in item and "pageviews" in item:
                            data_points.append(TimeseriesDataPoint(
                                date=item["date"],
                                pageviews=item["pageviews"]
                            ))
            
            result = TimeseriesOut(configured=True, data=data_points)
            if redis:
                try:
                    await redis.setex(cache_key, 60, json.dumps(result.model_dump()))
                except Exception:
                    pass
            return result
    except Exception as exc:
        logger.warning("DataFast timeseries call failed: %s", exc)
        return TimeseriesOut(configured=True, data=[])


@router.get("/top-clicked", response_model=list[TopClickedListingOut])
async def get_top_clicked(db: Annotated[AsyncSession, Depends(get_db)]) -> list[TopClickedListingOut]:
    # Exclude sponsors from the top clicked list
    from app.api.v1.routes.boards import SPONSOR_HANDLES, SPONSOR_IDS
    from sqlalchemy import String

    result = await db.execute(
        select(Listing)
        .where(
            Listing.status == "active",
            Listing.deleted_at.is_(None),
            ~Listing.handle.in_(SPONSOR_HANDLES),
            ~Listing.id.cast(String).in_(SPONSOR_IDS),
            Listing.clickthroughs > 0
        )
        .order_by(Listing.clickthroughs.desc())
        .limit(10)
    )
    listings = list(result.scalars())

    if not listings:
        return []

    listing_ids = [l.id for l in listings]
    entries_result = await db.execute(
        select(BoardEntry.listing_id, BoardEntry.paid_units)
        .where(
            BoardEntry.listing_id.in_(listing_ids),
            BoardEntry.status == "active",
            BoardEntry.deleted_at.is_(None)
        )
        .order_by(BoardEntry.paid_units.desc())
    )
    
    price_map = {}
    for l_id, paid_units in entries_result.all():
        if l_id not in price_map:
            # First one is the highest because of desc()
            price_map[l_id] = paid_units

    out = []
    for l in listings:
        price_b = None
        if l.id in price_map:
            price_b = f"{price_map[l.id] / 1000:g}"
        out.append(TopClickedListingOut(
            id=l.id,
            name=l.name,
            handle=l.handle,
            logo_url=l.logo_url,
            clickthroughs=l.clickthroughs,
            current_price_b=price_b
        ))
    return out
