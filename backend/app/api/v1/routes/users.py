import os
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
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


@router.get("/admin/overview")
async def get_admin_users_overview(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_internal_token: Annotated[str | None, Header(alias="x-internal-token")] = None,
    caller_tg_id: int | None = Query(None),
    secret_key: str | None = Query(None),
):
    """Internal admin endpoint to fetch all users, their balances, and their listings.

    Protected by:
    1. Valid X-Internal-Token or secret_key matching INTERNAL_API_TOKEN / SECRET_KEY
    AND
    2. Either caller_tg_id is an admin (is_admin=True in DB, or in ADMIN_TG_IDS),
       or valid secret_key argument provided.
    """
    # Check token
    token = x_internal_token if isinstance(x_internal_token, str) else None
    if not token and isinstance(secret_key, str):
        token = secret_key

    if not token or (token != settings.INTERNAL_API_TOKEN and token != settings.SECRET_KEY):
        raise HTTPException(status_code=403, detail="Forbidden: Invalid internal token")

    # If caller_tg_id provided, verify caller is authorized admin
    if isinstance(caller_tg_id, int):
        admin_ids_raw = os.getenv("ADMIN_TG_IDS", "")
        admin_ids = [int(x.strip()) for x in admin_ids_raw.split(",") if x.strip().isdigit()]
        has_secret = isinstance(secret_key, str) and secret_key in {settings.INTERNAL_API_TOKEN, settings.SECRET_KEY}
        is_allowed = caller_tg_id in admin_ids or has_secret

        if not is_allowed:
            # Check DB for is_admin flag
            user_stmt = select(User).where(User.telegram_id == caller_tg_id)
            user_res = await db.execute(user_stmt)
            caller_user = user_res.scalar_one_or_none()
            if caller_user and caller_user.is_admin:
                is_allowed = True

        if not is_allowed:
            raise HTTPException(status_code=403, detail="Forbidden: User is not an authorized administrator")

    # Fetch all users
    users_stmt = select(User).order_by(User.balance.desc(), User.created_at.desc())
    users_res = await db.execute(users_stmt)
    users = list(users_res.scalars())

    # Fetch all non-deleted listings
    listings_stmt = (
        select(Listing)
        .where(Listing.deleted_at.is_(None))
        .order_by(Listing.created_at.desc())
    )
    listings_res = await db.execute(listings_stmt)
    all_listings = list(listings_res.scalars())

    user_listings_map: dict[str, list[dict]] = {}
    for listing_item in all_listings:
        if not listing_item.owner_id:
            continue
        key = str(listing_item.owner_id)
        if key not in user_listings_map:
            user_listings_map[key] = []
        user_listings_map[key].append({
            "id": str(listing_item.id),
            "name": listing_item.name,
            "handle": listing_item.handle,
            "status": listing_item.status,
            "subscribers": listing_item.subscribers,
        })

    items = []
    for u in users:
        u_listings = user_listings_map.get(str(u.id), [])
        bal_b = u.balance
        items.append({
            "id": str(u.id),
            "telegram_id": u.telegram_id,
            "username": u.username,
            "first_name": u.first_name,
            "balance_b": bal_b,
            "balance_som": f"{bal_b * 1000:,}".replace(",", " "),
            "is_admin": u.is_admin,
            "listings_count": len(u_listings),
            "listings": u_listings,
        })

    return {
        "total_users": len(items),
        "total_listings": len(all_listings),
        "users": items,
    }

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
            logo_url=listing.logo_url,
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
    target_rank: int = 1
    period_type: str = "all_time"
    logo_url: str | None = None

class UpdateListingRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    logo_url: str | None = None

@router.post("/me/listings")
async def create_listing(
    req: CreateListingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.models.category import Category
    from app.models.listing import Listing
    from app.models.board import Board, BoardEntry
    from app.models.ledger import LedgerEntry
    from app.core.periods import get_period_bounds, now_tashkent
    import random
    
    if req.kind != "channel":
        raise HTTPException(status_code=400, detail="Hozircha faqat Telegram kanallar qo'shish mumkin")
        
    # Check category
    result = await db.execute(select(Category).where(Category.slug == req.category_slug))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=400, detail="Category not found")
        
    # If claim_now is True, check board and exact price for target_rank
    charge_b = 1
    target_rank = max(1, req.target_rank)
    board = None
    if req.claim_now:
        ref = now_tashkent()
        period_type = req.period_type or "all_time"
        starts_at, ends_at, period_key = get_period_bounds(period_type, ref)
        board_result = await db.execute(
            select(Board).where(
                Board.period_type == period_type,
                Board.period_key == period_key,
                Board.status == "active",
            )
        )
        board = board_result.scalar_one_or_none()
        if not board:
            board = Board(
                period_type=period_type,
                period_key=period_key,
                starts_at=starts_at,
                ends_at=ends_at,
                status="active",
            )
            db.add(board)
            await db.flush()

        entries_result = await db.execute(
            select(BoardEntry)
            .where(BoardEntry.board_id == board.id, BoardEntry.status == "active")
            .order_by(BoardEntry.paid_units.desc(), BoardEntry.entered_at.asc())
        )
        active_entries = list(entries_result.scalars())

        if target_rank <= len(active_entries):
            holder = active_entries[target_rank - 1]
            charge_b = (holder.paid_units // 1000) + 1
        else:
            charge_b = 1

        if user.balance < charge_b:
            raise HTTPException(
                status_code=400,
                detail=f"Mablag' yetarli emas. #{target_rank}-o'rin uchun balansingizda kamida {charge_b} B bo'lishi kerak"
            )
        user.balance -= charge_b

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

    # Auto-fetch subscriber count and channel photo from Telegram Bot API if public channel
    subscribers = 0
    logo_url = req.logo_url
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

        if not logo_url:
            from app.api.v1.routes.uploads import fetch_and_save_telegram_avatar
            try:
                logo_url = await fetch_and_save_telegram_avatar(proper_handle)
            except Exception:
                pass

    listing = Listing(
        kind=req.kind,
        handle=proper_handle,
        name=req.name,
        description=req.description,
        url=proper_url,
        logo_url=logo_url,
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

    if req.claim_now and board:
        board_entry = BoardEntry(
            board_id=board.id,
            listing_id=listing.id,
            paid_units=charge_b * 1000,
            entered_at=now_tashkent(),
            status="active"
        )
        db.add(board_entry)
        await db.flush()

        ledger_entry = LedgerEntry(
            user_id=user.id,
            delta_units=-charge_b,
            kind="claim_rank",
            ref_type="board_entry",
            ref_id=str(board_entry.id),
            balance_after=user.balance,
        )
        db.add(ledger_entry)

    await db.commit()
    await db.refresh(listing)
    
    return {
        "id": listing.id,
        "claimed": req.claim_now,
        "charge_b": charge_b,
        "target_rank": target_rank if req.claim_now else None,
        "new_balance": user.balance,
        "logo_url": listing.logo_url,
    }


@router.patch("/me/listings/{listing_id}")
async def update_my_listing(
    listing_id: str,
    req: UpdateListingRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    from uuid import UUID
    try:
        lid = UUID(listing_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Yaroqsiz listing ID")

    stmt = select(Listing).where(
        Listing.id == lid,
        Listing.owner_id == current_user.id,
        Listing.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Kanal topilmadi yoki unga egalik huquqingiz yo'q")

    if req.name is not None:
        listing.name = req.name.strip()
    if req.description is not None:
        listing.description = req.description.strip()
    if req.logo_url is not None:
        listing.logo_url = req.logo_url.strip() or None

    await db.commit()
    await db.refresh(listing)
    return {"status": "ok", "id": str(listing.id), "logo_url": listing.logo_url}

