from __future__ import annotations
import logging
from typing import Any, Tuple
import httpx

from app.core.config import get_settings
from app.core.redis import redis_client

logger = logging.getLogger(__name__)

REDIS_TOKEN_KEY = "inpay_bearer_token"
TOKEN_TTL_SECONDS = 23 * 3600  # ~23 hours


class InPayError(Exception):
    """Base exception for inPAY integration errors."""
    pass


async def get_inpay_bearer_token(force_refresh: bool = False) -> str:
    """Fetch or return cached bearer token from inPAY authorization API."""
    settings = get_settings()
    if not settings.INPAY_MERCHANT_ID or not settings.INPAY_MERCHANT_TOKEN:
        raise InPayError("inPAY merchant credentials are not configured")

    redis = redis_client
    if redis and not force_refresh:
        try:
            cached = await redis.get(REDIS_TOKEN_KEY)
            if cached:
                token_str = cached.decode() if isinstance(cached, bytes) else str(cached)
                if token_str:
                    return token_str
        except Exception as e:
            logger.warning("Redis error reading inPAY token: %s", e)

    # Fetch fresh bearer token from inPAY
    auth_url = f"{settings.INPAY_BASE_URL.rstrip('/')}/authorization/"
    params = {
        "merchant_id": settings.INPAY_MERCHANT_ID,
        "merchant_token": settings.INPAY_MERCHANT_TOKEN,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(auth_url, params=params)
            if not res.is_success:
                raise InPayError(f"inPAY authorization failed with status {res.status_code}")
            data = res.json()
    except Exception as e:
        if isinstance(e, InPayError):
            raise
        raise InPayError(f"Network error during inPAY authorization: {e}") from e

    # inPAY can return token in data.token, bearer_token, or token
    token = None
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], dict):
            token = data["data"].get("token") or data["data"].get("bearer_token")
        if not token:
            token = data.get("bearer_token") or data.get("token")

    if not token:
        raise InPayError("No bearer token found in inPAY authorization response")

    if redis:
        try:
            await redis.setex(REDIS_TOKEN_KEY, TOKEN_TTL_SECONDS, token)
        except Exception as e:
            logger.warning("Redis error caching inPAY token: %s", e)

    return token


async def create_inpay_order(
    amount_uzs: int,
    description: str,
    callback_url: str | None = None,
    return_url: str | None = None,
) -> Tuple[str, str]:
    """
    Create a hosted checkout order on inPAY.
    Returns (order_id, pay_url).
    """
    settings = get_settings()
    cb_url = callback_url or settings.INPAY_CALLBACK_URL
    ret_url = return_url or settings.INPAY_RETURN_URL

    token = await get_inpay_bearer_token()
    create_url = f"{settings.INPAY_BASE_URL.rstrip('/')}/create/"

    payload = {
        "merchant_id": settings.INPAY_MERCHANT_ID,
        "token": settings.INPAY_MERCHANT_TOKEN,
        "amount": amount_uzs,
        "description": description,
        "callback_url": cb_url,
        "return_url": ret_url,
    }

    for attempt in range(2):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(create_url, json=payload, headers=headers)
                if res.status_code == 401 and attempt == 0:
                    # Token expired, refresh and retry once
                    token = await get_inpay_bearer_token(force_refresh=True)
                    continue

                if not res.is_success:
                    raise InPayError(f"inPAY create order failed ({res.status_code}): {res.text}")

                data = res.json()
                break
        except Exception as e:
            if isinstance(e, InPayError):
                raise
            raise InPayError(f"Network error creating inPAY order: {e}") from e
    else:
        raise InPayError("Failed to create inPAY order after retry")

    order_id = None
    pay_url = None

    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], dict):
            order_id = data["data"].get("order_id")
            pay_url = data["data"].get("pay_url")
        if not order_id:
            order_id = data.get("order_id")
        if not pay_url:
            pay_url = data.get("pay_url")

    if not order_id or not pay_url:
        raise InPayError(f"Invalid order response from inPAY: {data}")

    return str(order_id), str(pay_url)


async def verify_inpay_transaction(order_id: str) -> dict[str, Any]:
    """
    Query inPAY GET /transactions/?order_id= to verify transaction state server-to-server.
    Returns parsed transaction info: { 'status': str, 'amount': int, 'transaction_id': str | None }
    """
    settings = get_settings()
    token = await get_inpay_bearer_token()
    tx_url = f"{settings.INPAY_BASE_URL.rstrip('/')}/transactions/"

    for attempt in range(2):
        headers = {"Authorization": f"Bearer {token}"}
        params = {"order_id": order_id}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(tx_url, params=params, headers=headers)
                if res.status_code == 401 and attempt == 0:
                    token = await get_inpay_bearer_token(force_refresh=True)
                    continue

                if not res.is_success:
                    raise InPayError(f"inPAY transaction verification failed ({res.status_code}): {res.text}")

                data = res.json()
                break
        except Exception as e:
            if isinstance(e, InPayError):
                raise
            raise InPayError(f"Network error verifying inPAY transaction: {e}") from e
    else:
        raise InPayError("Failed to verify inPAY transaction after retry")

    # inPAY transactions can return list or dict
    tx_data = data
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
            tx_data = data["data"][0]
        elif "data" in data and isinstance(data["data"], dict):
            tx_data = data["data"]
    elif isinstance(data, list) and len(data) > 0:
        tx_data = data[0]

    status = tx_data.get("status") if isinstance(tx_data, dict) else None
    amount = tx_data.get("amount") if isinstance(tx_data, dict) else None
    transaction_id = tx_data.get("transaction_id") or tx_data.get("id") if isinstance(tx_data, dict) else None

    return {
        "status": str(status) if status else "unknown",
        "amount": int(amount) if amount is not None else 0,
        "transaction_id": str(transaction_id) if transaction_id else None,
        "raw": tx_data,
    }
