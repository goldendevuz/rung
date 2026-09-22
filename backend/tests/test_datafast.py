"""Tests for DataFast server-side payment tracking service and failure resilience."""
from __future__ import annotations
import os
import pytest
from unittest.mock import patch
import httpx

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://rung:rung@localhost:5432/rung")
os.environ.setdefault("SECRET_KEY", "testsecretkey000000000000000000000000000000000000000000000000")
os.environ.setdefault("INTERNAL_API_TOKEN", "testtoken")
os.environ["DATAFAST_API_KEY"] = "df_test_key_1234567890abcdef"

from app.services.datafast import track_datafast_payment, APPROX_UZS_PER_USD


@pytest.mark.asyncio
async def test_track_datafast_payment_success() -> None:
    """Verify payload structure, headers, and USD conversion on success."""
    recorded_calls = []

    mock_resp = httpx.Response(
        200,
        json={"status": "ok", "id": "pay_123"},
        request=httpx.Request("POST", "https://datafa.st/api/v1/payments"),
    )

    async def mock_post(url, **kwargs):
        recorded_calls.append({"url": url, **kwargs})
        return mock_resp

    with patch("httpx.AsyncClient.post", side_effect=mock_post):
        result = await track_datafast_payment(
            amount_uzs=38400,
            order_id="rung_ord_test_001",
            datafast_visitor_id="vis_cookie_xyz789",
        )

    assert result == {"status": "ok", "id": "pay_123"}
    assert len(recorded_calls) == 1
    call = recorded_calls[0]
    assert call["url"] == "https://datafa.st/api/v1/payments"
    assert call["headers"]["Authorization"] == "Bearer df_test_key_1234567890abcdef"
    assert call["headers"]["Content-Type"] == "application/json"
    assert call["json"] == {
        "amount": 3.0,
        "currency": "USD",
        "transaction_id": "rung_ord_test_001",
        "datafast_visitor_id": "vis_cookie_xyz789",
    }


@pytest.mark.asyncio
async def test_track_datafast_payment_bad_url_resilience() -> None:
    """Verify that bad URLs or connection failures NEVER raise exceptions."""
    result = await track_datafast_payment(
        amount_uzs=50000,
        order_id="rung_ord_test_broken_url",
        datafast_visitor_id="vis_test",
        api_url="https://non-existent-datafast-domain-12345678.xyz/api/v1/payments",
    )
    assert result is None


@pytest.mark.asyncio
async def test_track_datafast_payment_500_resilience() -> None:
    """Verify that 500 server error from DataFast does not raise exception."""
    mock_resp = httpx.Response(
        500,
        json={"error": "Internal server error"},
        request=httpx.Request("POST", "https://datafa.st/api/v1/payments"),
    )

    with patch("httpx.AsyncClient.post", return_value=mock_resp):
        result = await track_datafast_payment(
            amount_uzs=12800,
            order_id="rung_ord_test_server_err",
            datafast_visitor_id="vis_test",
        )

    assert result is None


@pytest.mark.asyncio
async def test_track_datafast_no_api_key_skips() -> None:
    """Verify that if DATAFAST_API_KEY is empty, it skips cleanly."""
    with patch("app.services.datafast.get_settings") as mock_settings:
        mock_settings.return_value.DATAFAST_API_KEY = ""
        result = await track_datafast_payment(
            amount_uzs=20000,
            order_id="rung_ord_no_key",
        )
        assert result is None
