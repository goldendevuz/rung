from __future__ import annotations
from uuid import UUID
"""Pydantic schemas for public API v1 responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name_uz: str
    color: str
    icon: str | None
    listing_count: int = 0


# ── Listing (compact, for board rows) ─────────────────────────────────────────

class ListingMini(BaseModel):
    """Minimal listing info for board cards/lists."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    kind: str
    name: str
    handle: str
    verified: bool
    gradient_start: str
    gradient_end: str
    subscribers: int
    category_slug: str | None
    category_color: str | None

class ListingResponse(ListingMini):
    """Extended listing info for /listings/{public_id}."""
    description: str | None = None
    url: str | None = None
    claimed: bool = False
    free_label: str | None = None
    stats_daily: list[dict] = []
    clickthroughs: int = 0
    created_at: datetime | None = None


ListingCompact = ListingMini


class ListingDetail(ListingResponse):
    """Extended listing info for /listings/{public_id}."""
    status: str


# ── Board tab ─────────────────────────────────────────────────────────────────

class BoardTabOut(BaseModel):
    period_type: str
    active_count: int
    ends_at: datetime | None
    seconds_remaining: int | None


# ── Board entry (ranked) ──────────────────────────────────────────────────────

class BoardEntryOut(BaseModel):
    rank: int
    listing: ListingCompact
    paid_b: str          # Display string e.g. "25", "12.4"
    paid_units: int
    entered_at: datetime


class BoardPage(BaseModel):
    period_type: str
    period_key: str
    board_id: UUID
    entries: list[BoardEntryOut]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── Daily history ─────────────────────────────────────────────────────────────

class DailyHistoryBoard(BaseModel):
    period_key: str
    ends_at: datetime | None
    top3: list[BoardEntryOut]


# ── Quote ─────────────────────────────────────────────────────────────────────

class QuoteOut(BaseModel):
    board_id: UUID
    target_rank: int
    holder_paid_b: str
    holder_paid_units: int
    min_cost_b: str
    min_cost_units: int
    resulting_rank: int


# ── Stats ─────────────────────────────────────────────────────────────────────

class PublicStatsOut(BaseModel):
    total_listings: int
    total_entries: int
    online_now: int | None = None   # None when SHOW_LIVE_STATS=false
    visits_today: int | None = None  # None when SHOW_LIVE_STATS=false
    total_paid_units: int = 0


# ── Pagination helper ─────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
