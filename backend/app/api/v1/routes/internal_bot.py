import uuid
from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.listing import Listing
from app.models.subscriber_events import SubscriberEvent

router = APIRouter(prefix="/internal/bot", tags=["internal_bot"])

def verify_internal_api(
    x_internal_token: Annotated[str | None, Header(alias="x-internal-token")] = None,
) -> None:
    """Dependency to check the internal secret token for inter-service communication."""
    from app.core.config import get_settings
    settings = get_settings()
    
    token = x_internal_token if isinstance(x_internal_token, str) else None
    
    if not token or token != settings.INTERNAL_API_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid internal token")


class SubscriberEventPayload(BaseModel):
    telegram_chat_id: int
    telegram_user_id: int | None = None
    chat_username: str | None = None
    action: str  # 'join' or 'leave'
    source: str  # 'group' or 'channel'
    is_bot_admin: bool | None = None


@router.post(
    "/events/subscriber",
    dependencies=[Depends(verify_internal_api)],
)
async def handle_subscriber_event(
    payload: SubscriberEventPayload,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Receive subscriber events from the Telegram bot.
    Links the listing if not linked, updates bot_is_admin, and records the event.
    """
    # 1. Find Listing by telegram_chat_id
    from sqlalchemy.orm import joinedload
    result = await db.execute(
        select(Listing).options(joinedload(Listing.owner)).where(Listing.telegram_chat_id == payload.telegram_chat_id)
    )
    listing = result.scalar_one_or_none()

    # 2. If not found, try to link by chat_username
    if not listing and payload.chat_username:
        handle = payload.chat_username.lstrip("@").lower()
        # Find verified/claimed listing matching the handle
        result = await db.execute(
            select(Listing).options(joinedload(Listing.owner)).where(
                func.lower(func.replace(Listing.handle, "@", "")) == handle,
                Listing.claimed == True,
            )
        )
        listing = result.scalar_one_or_none()
        
        if listing:
            # Link it!
            listing.telegram_chat_id = payload.telegram_chat_id

    # 3. Insert the event regardless of whether we found a listing
    listing_id = listing.id if listing else None
    owner_telegram_id = listing.owner.telegram_id if listing and listing.owner else None
    listing_name = listing.name if listing else None

    # Update bot_is_admin if provided and listing exists
    if listing and payload.is_bot_admin is not None:
        listing.bot_is_admin = payload.is_bot_admin

    event = SubscriberEvent(
        listing_id=listing_id,
        telegram_chat_id=payload.telegram_chat_id,
        telegram_user_id=payload.telegram_user_id,
        action=payload.action,
        source=payload.source,
    )
    db.add(event)
    await db.commit()

    return {
        "status": "ok",
        "owner_telegram_id": owner_telegram_id,
        "listing_name": listing_name
    }
