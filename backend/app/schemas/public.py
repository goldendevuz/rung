"""Pydantic schemas for public API v1 responses."""
from __future__ import annotations

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

class ListingCompact(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    handle: str
    name: str
    description: str | None
    category_slug: str | None
    category_color: str | None
    subscribers: int
    verified: bool
    claimed: bool
    free_label: str | None
    gradient_start: str
    gradient_end: str
    clickthroughs: int = 0
    created_at: datetime


class ListingDetail(ListingCompact):
    """Extended listing info for /listings/{slug}."""
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
    board_id: int
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
    board_id: int
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


# ── Pagination helper ─────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
