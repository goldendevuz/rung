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
    """Proxy Telegram user profile photo."""
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getUserProfilePhotos?user_id={tg_id}&limit=1")
        if not res.is_success:
            raise HTTPException(status_code=404, detail="Not found")
            
        data = res.json()
        if not data.get("ok") or not data.get("result", {}).get("photos"):
            raise HTTPException(status_code=404, detail="No photo")
            
        file_id = data["result"]["photos"][0][-1]["file_id"]
        res = await client.get(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile?file_id={file_id}")
        if not res.is_success:
            raise HTTPException(status_code=404, detail="Not found")
            
        data = res.json()
        file_path = data["result"]["file_path"]
        
        file_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}"
        req = client.build_request("GET", file_url)
        r = await client.send(req, stream=True)
        return StreamingResponse(r.aiter_raw(), media_type="image/jpeg")
