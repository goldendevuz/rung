"""S1 logic tests: rank derivation, quote math, pagination, periods."""
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

import httpx
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
import os

os.environ.setdefault('DATABASE_URL', 'postgresql+asyncpg://rung:rung@localhost:5432/rung')
os.environ.setdefault('SECRET_KEY', 'testsecretkey000000000000000000000000000000000000000000000000')
os.environ.setdefault('INTERNAL_API_TOKEN', 'testtoken')

from app.core.periods import get_period_bounds, TZ, seconds_until_period_end
from app.core.money import units_to_b_display, b_to_units
from app.main import app


def test_money_helpers():
    assert b_to_units(25) == 25000
    assert units_to_b_display(25000) == "25"
    assert units_to_b_display(12400) == "12.4"
    assert units_to_b_display(200) == "0.2"


def test_period_bounds_daily():
    ref = datetime(2026, 9, 20, 15, 30, tzinfo=TZ)
    starts_at, ends_at, key = get_period_bounds("daily", ref)
    assert key == "2026-09-20"
    assert starts_at == datetime(2026, 9, 20, 0, 0, tzinfo=TZ).astimezone(timezone.utc)
    assert ends_at.year == 2026
    assert ends_at.month == 9
    assert ends_at.day == 20


def test_period_bounds_seasonal():
    ref = datetime(2026, 1, 15, tzinfo=TZ)
    _, _, key = get_period_bounds("seasonal", ref)
    assert key == "2025-S12"

    ref2 = datetime(2026, 9, 20, tzinfo=TZ)
    _, _, key2 = get_period_bounds("seasonal", ref2)
    assert key2 == "2026-S09"


def test_seconds_until_period_end():
    ref = datetime(2026, 9, 20, 23, 59, 50, tzinfo=TZ)
    secs = seconds_until_period_end("daily", ref)
    assert secs == 9


@pytest.mark.asyncio
async def test_all_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        # 1. test_tab_visibility
        resp = await ac.get('/api/v1/boards/tabs')
        assert resp.status_code == 200
        tabs = resp.json()
        assert isinstance(tabs, list)
        types = [t['period_type'] for t in tabs]
        assert 'seasonal' not in types

        # 2. test_rank_derivation_and_pagination
        resp = await ac.get('/api/v1/boards/all_time/current?page=1')
        assert resp.status_code == 200
        data = resp.json()
        entries = data['entries']
        assert len(entries) > 0
        for i in range(len(entries) - 1):
            # Rank derivation with ties: paid_units DESC, then entered_at ASC
            paid1 = entries[i]['paid_units']
            paid2 = entries[i+1]['paid_units']
            assert paid1 >= paid2
            if paid1 == paid2:
                # ties broken by entered_at ASC
                t1 = datetime.fromisoformat(entries[i]['entered_at'].replace('Z', '+00:00'))
                t2 = datetime.fromisoformat(entries[i+1]['entered_at'].replace('Z', '+00:00'))
                assert t1 <= t2
        assert data['page'] == 1
        assert data['total'] > 0
        
        # 2.b pagination (page 2)
        if data['total_pages'] > 1:
            p2_resp = await ac.get('/api/v1/boards/all_time/current?page=2')
            assert p2_resp.status_code == 200
            p2_data = p2_resp.json()
            assert p2_data['page'] == 2
            assert len(p2_data['entries']) > 0
            assert p2_data['entries'][0]['rank'] == 13 # since PAGE_SIZE is 12

        # 3. test_category_filter
        resp = await ac.get('/api/v1/boards/all_time/current?category=texnologiya')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            cat_data = resp.json()
            for e in cat_data['entries']:
                assert e['listing']['category_slug'] == 'texnologiya'

        # 4. test_search
        resp = await ac.get('/api/v1/boards/all_time/current?q=uz')
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            search_data = resp.json()
            for e in search_data['entries']:
                assert 'uz' in e['listing']['name'].lower() or 'uz' in e['listing']['handle'].lower()

        # 5. test_quote_math
        board_id = data['board_id']
        if entries:
            quote_resp = await ac.get(f'/api/v1/boards/{board_id}/quote?target_rank=1')
            assert quote_resp.status_code == 200
            quote_data = quote_resp.json()
            holder_paid = quote_data['holder_paid_units']
            assert quote_data['min_cost_units'] == holder_paid + 1000
            # Explicitly check seeded data value
            if data['period_type'] == 'all_time':
                assert quote_data['min_cost_units'] == 26000

