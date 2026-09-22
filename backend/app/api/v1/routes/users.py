from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.listing import Listing
from app.models.user import User
from app.schemas.public import ListingDetail
from app.core.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/listings", response_model=list[ListingDetail])
async def get_my_listings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ListingDetail]:
    """Get all listings owned by the current authenticated user."""
    stmt = (
        select(Listing)
        .where(Listing.owner_id == current_user.id, Listing.deleted_at.is_(None))
        .options(selectinload(Listing.category))
        .order_by(Listing.created_at.desc())
    )
    result = await db.execute(stmt)
    listings = result.scalars().all()

    return [
        ListingDetail(
            id=listing.id,
            kind=listing.kind,
            handle=listing.handle,
            name=listing.name,
            description=listing.description,
            url=listing.url or f"https://t.me/{listing.handle.lstrip('@')}",
            category_slug=listing.category.slug if listing.category else None,
            category_color=listing.category.color if listing.category else None,
            subscribers=listing.subscribers,
            verified=listing.verified,
            claimed=listing.claimed,
            free_label=listing.free_label,
            gradient_start=listing.gradient_start,
            gradient_end=listing.gradient_end,
            clickthroughs=0,
            created_at=listing.created_at,
            status=listing.status,
        )
        for listing in listings
    ]

@router.get("/avatar/{tg_id}")
async def get_avatar(tg_id: int):
    """Proxy Telegram user profile photo with caching."""
    from fastapi import Response
    from app.core.redis import get_redis

    cache_key = f"tg_avatar:{tg_id}"
    redis = await get_redis()
    if redis:
        try:
            cached = await redis.get(cache_key)
            if cached:
                return Response(
                    content=cached,
                    media_type="image/jpeg",
                    headers={"Cache-Control": "public, max-age=86400"}
                )
        except Exception:
            pass

    if not settings.BOT_TOKEN:
        raise HTTPException(status_code=404, detail="No bot token")

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            res = await client.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getUserProfilePhotos?user_id={tg_id}&limit=1")
            if not res.is_success:
                raise HTTPException(status_code=404, detail="Not found")
                
            data = res.json()
            if not data.get("ok") or not data.get("result", {}).get("photos") or not data["result"]["photos"][0]:
                raise HTTPException(status_code=404, detail="No photo")
                
            file_id = data["result"]["photos"][0][-1]["file_id"]
            res = await client.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile?file_id={file_id}")
            if not res.is_success:
                raise HTTPException(status_code=404, detail="Not found")
                
            data = res.json()
            file_path = data.get("result", {}).get("file_path")
            if not file_path:
                raise HTTPException(status_code=404, detail="No file path")
            
            file_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}"
            r = await client.get(file_url)
            if not r.is_success:
                raise HTTPException(status_code=404, detail="Not found")
                
            content = r.content
            if redis and content:
                try:
                    await redis.setex(cache_key, 86400, content)
                except Exception:
                    pass

            return Response(
                content=content,
                media_type="image/jpeg",
                headers={"Cache-Control": "public, max-age=86400"}
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Could not fetch avatar")
from pydantic import BaseModel

class CreateListingRequest(BaseModel):
    kind: str
    handle: str
    name: str
    description: str | None = None
    category_slug: str
    claim_now: bool = True

@router.post("/me/listings")
async def create_listing(
    req: CreateListingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.models.category import Category
    from app.models.listing import Listing
    from app.models.board import Board, BoardEntry
    from app.core.periods import get_period_bounds, now_tashkent
    import random
    
    if req.kind != "channel":
        raise HTTPException(status_code=400, detail="Hozircha faqat Telegram kanallar qo'shish mumkin")
        
    # Check category
    result = await db.execute(select(Category).where(Category.slug == req.category_slug))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=400, detail="Category not found")
        
    # If claim_now is True, check user balance
    if req.claim_now:
        if user.balance < 1:
            raise HTTPException(status_code=400, detail="Mablag' yetarli emas. Balansingizda kamida 1 B bo'lishi kerak")
        user.balance -= 1

    # Generate random gradient for missing avatars
    colors = ["#2563EB", "#1E3A8A", "#7C3AED", "#4C1D95", "#059669", "#064E3B", "#D97706", "#92400E"]
    g_start = random.choice(colors)
    g_end = random.choice(colors)
    
    # Clean handle and build URL
    raw_handle = req.handle.strip()
    clean_handle = raw_handle
    for prefix in [
        "https://t.me/", "http://t.me/", "t.me/",
        "https://telegram.me/", "http://telegram.me/", "telegram.me/"
    ]:
        if clean_handle.lower().startswith(prefix):
            clean_handle = clean_handle[len(prefix):]
            break
    clean_handle = clean_handle.lstrip("@").strip("/")
    proper_handle = f"@{clean_handle}" if clean_handle else raw_handle
    proper_url = f"https://t.me/{clean_handle}" if clean_handle else f"https://t.me/{raw_handle}"

    # Auto-fetch subscriber count from Telegram Bot API if public channel
    subscribers = 0
    if clean_handle and settings.BOT_TOKEN:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(
                    f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getChatMemberCount",
                    params={"chat_id": proper_handle}
                )
                if res.is_success:
                    data = res.json()
                    if data.get("ok"):
                        subscribers = int(data.get("result", 0))
        except Exception:
            pass

    listing = Listing(
        kind=req.kind,
        handle=proper_handle,
        name=req.name,
        description=req.description,
        url=proper_url,
        subscribers=subscribers,
        category_id=cat.id,
        owner_id=user.id,
        status="active",
        verified=False,
        claimed=True,
        gradient_start=g_start,
        gradient_end=g_end
    )
    db.add(listing)
    await db.flush()

    if req.claim_now:
        ref = now_tashkent()
        starts_at, ends_at, period_key = get_period_bounds("all_time", ref)
        board_result = await db.execute(
            select(Board).where(
                Board.period_type == "all_time",
                Board.period_key == period_key,
                Board.status == "active",
            )
        )
        board = board_result.scalar_one_or_none()
        if not board:
            board = Board(
                period_type="all_time",
                period_key=period_key,
                starts_at=starts_at,
                ends_at=ends_at,
                status="active",
            )
            db.add(board)
            await db.flush()

        board_entry = BoardEntry(
            board_id=board.id,
            listing_id=listing.id,
            paid_units=1000,
            entered_at=now_tashkent(),
            status="active"
        )
        db.add(board_entry)

    await db.commit()
    await db.refresh(listing)
    
    return {
        "id": listing.id,
        "claimed": req.claim_now,
        "new_balance": user.balance
    }

