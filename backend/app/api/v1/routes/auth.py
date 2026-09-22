import secrets
import json
from typing import Annotated
from urllib.parse import parse_qsl

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

from pydantic import BaseModel

from app.core.config import get_settings
from app.core.security import verify_telegram_init_data, create_session_token
from app.core.redis import get_redis
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])

class InitDataRequest(BaseModel):
    initData: str

@router.post("/telegram/miniapp")
async def telegram_miniapp_login(
    payload: InitDataRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Logs in using Telegram WebApp initData."""
    is_valid = verify_telegram_init_data(payload.initData, settings.BOT_TOKEN)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid initData")
    
    parsed = dict(parse_qsl(payload.initData, keep_blank_values=True))
    user_str = parsed.get("user")
    if not user_str:
        raise HTTPException(status_code=400, detail="No user in initData")
        
    try:
        tg_user = json.loads(user_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid user JSON")
        
    tg_id = tg_user.get("id")
    if not tg_id:
        raise HTTPException(status_code=400, detail="No telegram id")
        
    result = await db.execute(select(User).where(User.telegram_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(telegram_id=tg_id)
        db.add(user)
        
    user.username = tg_user.get("username")
    user.first_name = tg_user.get("first_name")
    user.photo_url = tg_user.get("photo_url")
    
    await db.commit()
    await db.refresh(user)
    
    token = create_session_token(user.id)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=settings.ENV == "prod",
        samesite="lax",
        max_age=30 * 86400,
    )
    
    return {"id": user.id, "telegram_id": user.telegram_id, "username": user.username, "first_name": user.first_name, "photo_url": user.photo_url}


@router.post("/telegram/start")
async def telegram_start_login(
    request: Request,
    redis: redis.Redis = Depends(get_redis)
):
    """Generates a one-time token for deep-link login."""
    client_ip = request.client.host if request.client else "unknown"
    rl_key = f"rl:tg_start:{client_ip}"
    
    reqs = await redis.incr(rl_key)
    if reqs == 1:
        await redis.expire(rl_key, 60)
    elif reqs > 5:
        raise HTTPException(status_code=429, detail="Too many requests")

    token = secrets.token_urlsafe(32)
    # TTL is 5 minutes = 300 seconds
    await redis.set(f"auth:tg:{token}", "pending", ex=300)
    
    return {"token": token, "expires_in": 300}


@router.get("/telegram/poll")
async def telegram_poll(
    token: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
    redis: redis.Redis = Depends(get_redis)
):
    """Polls the status of a login token."""
    key = f"auth:tg:{token}"
    status_val = await redis.get(key)
    
    if not status_val:
        raise HTTPException(status_code=410, detail="Token expired or not found")
        
    if status_val == "pending":
        # 202 Accepted means still processing
        return Response(status_code=status.HTTP_202_ACCEPTED)
        
    if status_val == "used":
        raise HTTPException(status_code=410, detail="Token already used")
        
    if status_val.startswith("confirmed:"):
        tg_id = int(status_val.split(":")[1])
        
        # Mark as used so it can't be reused
        await redis.set(key, "used", ex=60)
        
        result = await db.execute(select(User).where(User.telegram_id == tg_id))
        user = result.scalar_one_or_none()
        
        # If user wasn't found, this means they used the bot but somehow weren't upserted yet?
        # Let's upsert them here, though we only have their ID unless the bot saved more info.
        # But for now, bot will just provide ID.
        if not user:
            user = User(telegram_id=tg_id)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        session_token = create_session_token(user.id)
        response.set_cookie(
            key="session",
            value=session_token,
            httponly=True,
            secure=settings.ENV == "prod",
            samesite="lax",
            max_age=30 * 86400,
        )
        return {"id": user.id, "telegram_id": user.telegram_id, "username": user.username, "first_name": user.first_name, "photo_url": user.photo_url}


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "telegram_id": user.telegram_id, "username": user.username, "first_name": user.first_name, "photo_url": user.photo_url}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="session",
        httponly=True,
        secure=settings.ENV == "prod",
        samesite="lax",
    )
    return {"status": "ok"}
