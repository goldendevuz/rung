"""Listings API endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.listing import Listing
from app.models.stats import ListingStatsDaily
from app.schemas.public import ListingDetail

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/{public_id}", response_model=ListingDetail)
async def get_listing(
    public_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ListingDetail:
    """Get a single listing by public_id."""
    result = await db.execute(
        select(Listing)
        .where(Listing.public_id == public_id, Listing.deleted_at.is_(None))
        .options(selectinload(Listing.category))
    )
    listing = result.scalar_one_or_none()
    if listing is None or listing.status != "active":
        raise HTTPException(status_code=404, detail="Listing not found")

    # Total clickthroughs
    clicks_result = await db.execute(
        select(func.sum(ListingStatsDaily.clickthroughs)).where(
            ListingStatsDaily.listing_id == listing.id
        )
    )
    clickthroughs = int(clicks_result.scalar_one() or 0)

    return ListingDetail(
        public_id=listing.public_id,
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
        clickthroughs=clickthroughs,
        created_at=listing.created_at,
        status=listing.status,
    )
