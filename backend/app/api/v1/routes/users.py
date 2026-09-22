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
        r = await client.get(file_url)
        if not r.is_success:
            raise HTTPException(status_code=404, detail="Not found")
            
        from fastapi import Response
        return Response(content=r.content, media_type="image/jpeg")
from pydantic import BaseModel

class CreateListingRequest(BaseModel):
    kind: str
    handle: str
    name: str
    description: str | None = None
    category_slug: str

@router.post("/me/listings")
async def create_listing(
    req: CreateListingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from app.models.category import Category
    from app.models.listing import Listing
    import random
    
    if req.kind != "channel":
        raise HTTPException(status_code=400, detail="Hozircha faqat Telegram kanallar qo'shish mumkin")
        
    # Check category
    result = await db.execute(select(Category).where(Category.slug == req.category_slug))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=400, detail="Category not found")
        
    # Generate random gradient for missing avatars
    colors = ["#2563EB", "#1E3A8A", "#7C3AED", "#4C1D95", "#059669", "#064E3B", "#D97706", "#92400E"]
    g_start = random.choice(colors)
    g_end = random.choice(colors)
    
    listing = Listing(
        kind=req.kind,
        handle=req.handle,
        name=req.name,
        description=req.description,
        category_id=cat.id,
        owner_id=user.id,
        status="active",
        verified=False,
        claimed=True,
        gradient_start=g_start,
        gradient_end=g_end
    )
    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    
    return {"id": listing.id}
