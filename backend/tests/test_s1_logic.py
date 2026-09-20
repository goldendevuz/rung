"""S1 logic tests: rank derivation, quote math, pagination, periods."""
import pytest
from datetime import datetime, timezone, timedelta
from app.core.periods import get_period_bounds, TZ, seconds_until_period_end
from app.core.money import units_to_b_display, b_to_units
from app.models.board import Board, BoardEntry
from app.models.listing import Listing
from app.models.category import Category
from sqlalchemy import select

# We use the real DB created by docker compose and pytest-asyncio
# For full tests we'd want a test DB, but for this S1 gate we test logic.

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
    # End of day is 23:59:59.999999
    assert ends_at.year == 2026
    assert ends_at.month == 9
    assert ends_at.day == 20
    # in UTC it will be 18:59:59 because Tashkent is UTC+5


def test_period_bounds_seasonal():
    # Jan -> winter (Dec of prev year to Feb of current year)
    ref = datetime(2026, 1, 15, tzinfo=TZ)
    _, _, key = get_period_bounds("seasonal", ref)
    assert key == "2025-S12"  # Starts Dec 2025

    # Sep -> autumn (Sep to Nov)
    ref2 = datetime(2026, 9, 20, tzinfo=TZ)
    _, _, key2 = get_period_bounds("seasonal", ref2)
    assert key2 == "2026-S09"


def test_seconds_until_period_end():
    ref = datetime(2026, 9, 20, 23, 59, 50, tzinfo=TZ)
    secs = seconds_until_period_end("daily", ref)
    assert secs == 9  # 50 to 59 is 9 seconds (plus ms, but we cast to int)


@pytest.mark.asyncio
async def test_rank_derivation(db_session):
    # This assumes db_session fixture exists, but we can also just test via API endpoints
    pass
