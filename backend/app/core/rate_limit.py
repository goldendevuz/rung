from __future__ import annotations
import logging
from typing import Callable
from fastapi import HTTPException, Request
from app.core.redis import get_redis

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """Extract real client IP from reverse proxy headers or direct connection."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client:
        return request.client.host
    return "127.0.0.1"


async def check_rate_limit(
    request: Request,
    namespace: str,
    limit: int,
    window_seconds: int = 60,
    identifier: str | None = None,
) -> None:
    """
    Enforce a sliding/fixed window rate limit per client identifier in Redis.
    Raises HTTPException(429) if the limit is exceeded.
    """
    try:
        redis = await get_redis()
        client_id = identifier or get_client_ip(request)
        key = f"rl:{namespace}:{client_id}"

        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.ttl(key)
        current, ttl = await pipe.execute()

        if ttl < 0 or current == 1:
            await redis.expire(key, window_seconds)
            ttl = window_seconds

        if current > limit:
            retry_after = max(1, ttl)
            raise HTTPException(
                status_code=429,
                detail="Juda ko'p so'rov yuborildi. Iltimos, birozdan keyin qayta urinib ko'ring.",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Rate limiter Redis exception in %s: %s", namespace, e)


def rate_limit(namespace: str, limit: int, window_seconds: int = 60) -> Callable:
    """FastAPI Dependency for route-level rate limiting."""
    async def dependency(request: Request):
        await check_rate_limit(request, namespace, limit, window_seconds)
    return dependency
