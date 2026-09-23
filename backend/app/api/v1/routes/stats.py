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
                data_30d = resp_30d.json()
                v_30d = data_30d.get("visitors")
                if v_30d is None and isinstance(data_30d.get("data"), dict):
                    v_30d = data_30d["data"].get("visitors", 0)

            resp_today = await client.get(
                f"https://datafa.st/api/v1/analytics/overview?startAt={today_str}&endAt={today_str}",
                headers=headers,
            )
            v_today = 0
            if resp_today.status_code == 200:
                data_today = resp_today.json()
                v_today = data_today.get("visitors")
                if v_today is None and isinstance(data_today.get("data"), dict):
                    v_today = data_today["data"].get("visitors", 0)

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

