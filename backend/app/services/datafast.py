"""DataFast server-side payment tracking service."""
from __future__ import annotations

import logging
import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

DATAFAST_PAYMENTS_URL = "https://datafa.st/api/v1/payments"
# Approximate exchange rate: 1 USD = 12,800 UZS for analytics attribution
APPROX_UZS_PER_USD = 12800.0


async def track_datafast_payment(
    amount_uzs: int,
    order_id: str,
    datafast_visitor_id: str | None = None,
    api_url: str = DATAFAST_PAYMENTS_URL,
) -> dict | None:
    """Send a server-side payment event to DataFast for revenue attribution.

    Called ONLY after server-to-server verification succeeds.
    Failures are logged and never raise exceptions, ensuring payments are never blocked.
    """
    settings = get_settings()
    api_key = settings.DATAFAST_API_KEY
    if not api_key:
        logger.debug("DATAFAST_API_KEY is not configured; skipping DataFast payment event")
        return None

    # Convert UZS to USD (approximate for analytics attribution)
    amount_usd = max(0.01, round(amount_uzs / APPROX_UZS_PER_USD, 2))

    payload = {
        "amount": amount_usd,
        "currency": "USD",
        "transaction_id": order_id,
        "datafast_visitor_id": datafast_visitor_id or "anonymous",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                api_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            if resp.status_code in (200, 201):
                logger.info("DataFast payment tracked: order=%s, amount_usd=%s", order_id, amount_usd)
                return resp.json()
            else:
                logger.warning(
                    "DataFast payment tracking returned %s: %s",
                    resp.status_code,
                    resp.text,
                )
                return None
    except Exception as exc:
        logger.warning("DataFast payment tracking failed for order %s: %s", order_id, exc)
        return None
