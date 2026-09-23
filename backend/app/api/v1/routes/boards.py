"""Public boards API endpoints."""
from __future__ import annotations

import math
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.money import units_to_b_display
from app.core.periods import get_period_bounds, now_tashkent, seconds_until_period_end
from app.db.session import get_db
from app.models.board import Board, BoardEntry
from app.models.category import Category
from app.models.listing import Listing
from app.models.stats import ListingStatsDaily
from app.models.ledger import LedgerEntry
import uuid
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.public import (
    ActivityItemOut,
    BoardEntryOut,
    BoardPage,
    BoardTabOut,
    DailyHistoryBoard,
    ListingCompact,
    QuoteOut,
)

router = APIRouter(prefix="/boards", tags=["boards"])

PAGE_SIZE = 12


def _listing_to_compact(listing: Listing, clickthroughs: int = 0) -> ListingCompact:
    return ListingCompact(
        id=listing.id,
        kind=listing.kind,
        handle=listing.handle,
        name=listing.name,
        description=listing.description,
        category_slug=listing.category.slug if listing.category else None,
        category_color=listing.category.color if listing.category else None,
        subscribers=listing.subscribers,
        verified=listing.verified,
        claimed=listing.claimed,
        free_label=listing.free_label,
        logo_url=listing.logo_url,
        gradient_start=listing.gradient_start,
        gradient_end=listing.gradient_end,
        clickthroughs=clickthroughs,
        created_at=listing.created_at,
    )


async def _get_clickthroughs_map(session: AsyncSession, listing_ids: list[int]) -> dict[int, int]:
    """Sum clickthroughs across all time for given listings."""
    if not listing_ids:
        return {}
    result = await session.execute(
        select(
            ListingStatsDaily.listing_id,
            func.sum(ListingStatsDaily.clickthroughs).label("total"),
        )
        .where(ListingStatsDaily.listing_id.in_(listing_ids))
        .group_by(ListingStatsDaily.listing_id)
    )
    return {row.listing_id: int(row.total or 0) for row in result}


@router.get("/tabs", response_model=list[BoardTabOut])
async def get_tabs(db: Annotated[AsyncSession, Depends(get_db)]) -> list[BoardTabOut]:
    """Return period tabs that have at least one active entry in the current board."""
    from app.core.periods import PERIOD_TYPES

    tabs: list[BoardTabOut] = []
    ref = now_tashkent()

    for period_type in PERIOD_TYPES:
        _, _, period_key = get_period_bounds(period_type, ref)

        # Find current board for this period
        board_result = await db.execute(
            select(Board).where(
                Board.period_type == period_type,
                Board.period_key == period_key,
                Board.status == "active",
            )
        )
        board = board_result.scalar_one_or_none()
        if board is None:
            continue

        # Count active entries
        count_result = await db.execute(
            select(func.count(BoardEntry.id)).where(
                BoardEntry.board_id == board.id,
                BoardEntry.status == "active",
            )
        )
        count = count_result.scalar_one() or 0
        if count == 0:
            continue

        tabs.append(
            BoardTabOut(
                period_type=period_type,
                active_count=count,
                ends_at=board.ends_at,
                seconds_remaining=seconds_until_period_end(period_type, ref),
            )
        )

    return tabs


@router.get("/{period_type}/current", response_model=BoardPage)
async def get_board_current(
    period_type: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    category: str | None = Query(None),
    q: str | None = Query(None),
) -> BoardPage:
    """Paginated ranked board for the current period."""
    from app.core.periods import PERIOD_TYPES

    if period_type not in PERIOD_TYPES:
        raise HTTPException(status_code=404, detail="Unknown period_type")

    ref = now_tashkent()
    _, _, period_key = get_period_bounds(period_type, ref)

    board_result = await db.execute(
        select(Board).where(
            Board.period_type == period_type,
            Board.period_key == period_key,
            Board.status == "active",
        )
    )
    board = board_result.scalar_one_or_none()
    if board is None:
        return BoardPage(
            period_type=period_type,
            period_key=period_key,
            board_id="00000000-0000-0000-0000-000000000000",
            entries=[],
            total=0,
            page=page,
            page_size=PAGE_SIZE,
            total_pages=1,
        )

    # Base query: active entries with listing + category
    base_q = (
        select(BoardEntry)
        .where(BoardEntry.board_id == board.id, BoardEntry.status == "active")
        .join(BoardEntry.listing)
        .options(selectinload(BoardEntry.listing).selectinload(Listing.category))
    )

    if category:
        base_q = base_q.join(Listing.category).where(Category.slug == category)

    if q:
        pattern = f"%{q.lower()}%"
        base_q = base_q.where(
            func.lower(Listing.name).like(pattern) | func.lower(Listing.handle).like(pattern)
        )

    # Count total
    count_q = select(func.count()).select_from(base_q.subquery())
    total = (await db.execute(count_q)).scalar_one() or 0

    # Ranked (derived): paid_units DESC, entered_at ASC
    entries_result = await db.execute(
        base_q.order_by(BoardEntry.paid_units.desc(), BoardEntry.entered_at.asc())
        .offset((page - 1) * PAGE_SIZE)
        .limit(PAGE_SIZE)
    )
    entries = list(entries_result.scalars())

    listing_ids = [e.listing_id for e in entries]
    click_map = await _get_clickthroughs_map(db, listing_ids)

    global_offset = (page - 1) * PAGE_SIZE
    entry_outs = [
        BoardEntryOut(
            rank=global_offset + idx + 1,
            listing=_listing_to_compact(e.listing, click_map.get(e.listing_id, 0)),
            paid_b=units_to_b_display(e.paid_units),
            paid_units=e.paid_units,
            entered_at=e.entered_at,
        )
        for idx, e in enumerate(entries)
    ]

    return BoardPage(
        period_type=period_type,
        period_key=period_key,
        board_id=board.id,
        entries=entry_outs,
        total=total,
        page=page,
        page_size=PAGE_SIZE,
        total_pages=max(1, math.ceil(total / PAGE_SIZE)),
    )


@router.get("/daily/history", response_model=list[DailyHistoryBoard])
async def get_daily_history(db: Annotated[AsyncSession, Depends(get_db)]) -> list[DailyHistoryBoard]:
    """Return the top-3 entries of closed daily boards (most recent first)."""
    result = await db.execute(
        select(Board)
        .where(Board.period_type == "daily", Board.status == "closed")
        .order_by(Board.starts_at.desc())
        .limit(10)
    )
    closed_boards = list(result.scalars())

    history: list[DailyHistoryBoard] = []
    for board in closed_boards:
        entries_result = await db.execute(
            select(BoardEntry)
            .where(BoardEntry.board_id == board.id, BoardEntry.status == "active")
            .options(selectinload(BoardEntry.listing).selectinload(Listing.category))
            .order_by(BoardEntry.paid_units.desc(), BoardEntry.entered_at.asc())
            .limit(3)
        )
        entries = list(entries_result.scalars())
        listing_ids = [e.listing_id for e in entries]
        click_map = await _get_clickthroughs_map(db, listing_ids)

        top3 = [
            BoardEntryOut(
                rank=idx + 1,
                listing=_listing_to_compact(e.listing, click_map.get(e.listing_id, 0)),
                paid_b=units_to_b_display(e.paid_units),
                paid_units=e.paid_units,
                entered_at=e.entered_at,
            )
            for idx, e in enumerate(entries)
        ]
        history.append(
            DailyHistoryBoard(
                period_key=board.period_key,
                ends_at=board.ends_at,
                top3=top3,
            )
        )

    return history


@router.get("/activity", response_model=list[ActivityItemOut])
async def get_recent_activity(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(8, ge=1, le=20),
) -> list[ActivityItemOut]:
    """Return recent rank claims across boards (latest activity feed), excluding Rung and Fast Signals."""
    stmt = (
        select(BoardEntry)
        .options(selectinload(BoardEntry.listing))
        .where(
            BoardEntry.status.in_(["active", "replaced"]),
            BoardEntry.deleted_at.is_(None),
        )
        .order_by(BoardEntry.entered_at.desc())
        .limit(limit * 3)
    )
    result = await db.execute(stmt)
    entries = list(result.scalars())

    activity_items: list[ActivityItemOut] = []
    for e in entries:
        if not e.listing:
            continue
        handle_clean = (e.listing.handle or "").lower().lstrip("@").strip()
        name_clean = (e.listing.name or "").lower().strip()
        # Exclude Rung, Fast Signals, and Sponsor projects (SIPAGENTBOT, etc.) per user requirement
        if (
            handle_clean in {"rung_uz", "uz_fast_signals", "sipagentbot"}
            or "rung" in handle_clean
            or "fast_signals" in handle_clean
            or "fast signals" in name_clean
            or "sipagentbot" in handle_clean
            or "sipagentbot" in name_clean
        ):
            continue

        activity_items.append(
            ActivityItemOut(
                id=e.id,
                listing_id=e.listing.id,
                listing_name=e.listing.name,
                listing_handle=e.listing.handle,
                listing_logo_url=e.listing.logo_url,
                listing_gradient_start=e.listing.gradient_start,
                listing_gradient_end=e.listing.gradient_end,
                paid_b=units_to_b_display(e.paid_units),
                paid_units=e.paid_units,
                entered_at=e.entered_at,
            )
        )
        if len(activity_items) >= limit:
            break
    return activity_items


class CandidateRankOut(BaseModel):
    rank: int
    is_occupied: bool
    holder_name: str | None = None
    holder_handle: str | None = None
    holder_paid_b: int = 0
    price_b: int


@router.get("/{board_id}/candidates", response_model=list[CandidateRankOut])
async def get_candidates(
    board_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50),
    category: str | None = Query(None),
) -> list[CandidateRankOut]:
    """Get live pricing and occupant info for candidate ranks 1..limit, optionally filtered by category."""
    board = None
    try:
        b_uuid = uuid.UUID(board_id)
        result = await db.execute(select(Board).where(Board.id == b_uuid))
        board = result.scalar_one_or_none()
    except ValueError:
        ref = now_tashkent()
        _, _, period_key = get_period_bounds(board_id, ref)
        result = await db.execute(
            select(Board).where(
                Board.period_type == board_id,
                Board.period_key == period_key,
                Board.status == "active",
            )
        )
        board = result.scalar_one_or_none()

    active_entries: list[BoardEntry] = []
    if board:
        base_q = (
            select(BoardEntry)
            .where(BoardEntry.board_id == board.id, BoardEntry.status == "active")
            .join(BoardEntry.listing)
            .options(selectinload(BoardEntry.listing))
        )
        if category and category != "all":
            base_q = base_q.join(Listing.category).where(Category.slug == category)

        entries_result = await db.execute(
            base_q.order_by(BoardEntry.paid_units.desc(), BoardEntry.entered_at.asc())
        )
        active_entries = list(entries_result.scalars())

    candidates: list[CandidateRankOut] = []
    total_ranks = max(limit, len(active_entries) + 1)
    for r in range(1, total_ranks + 1):
        if r <= len(active_entries):
            e = active_entries[r - 1]
            paid_b = e.paid_units // 1000
            price_b = paid_b + 1  # occupant's price + 1 B
            candidates.append(
                CandidateRankOut(
                    rank=r,
                    is_occupied=True,
                    holder_name=e.listing.name if e.listing else None,
                    holder_handle=e.listing.handle if e.listing else None,
                    holder_paid_b=paid_b,
                    price_b=price_b,
                )
            )
        else:
            candidates.append(
                CandidateRankOut(
                    rank=r,
                    is_occupied=False,
                    holder_name=None,
                    holder_handle=None,
                    holder_paid_b=0,
                    price_b=1,
                )
            )
        if len(candidates) >= limit:
            break

    return candidates


@router.get("/{board_id}/quote", response_model=QuoteOut)
async def get_quote(
    board_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    target_rank: int = Query(..., ge=1),
    category: str | None = Query(None),
) -> QuoteOut:
    """Read-only quote: cost to claim target_rank on a board (by board UUID or period_type), optionally filtered by category."""
    board = None
    try:
        b_uuid = uuid.UUID(board_id)
        result = await db.execute(select(Board).where(Board.id == b_uuid))
        board = result.scalar_one_or_none()
    except ValueError:
        ref = now_tashkent()
        _, _, period_key = get_period_bounds(board_id, ref)
        result = await db.execute(
            select(Board).where(
                Board.period_type == board_id,
                Board.period_key == period_key,
                Board.status == "active",
            )
        )
        board = result.scalar_one_or_none()

    if board is None:
        return QuoteOut(
            board_id=board_id,
            target_rank=target_rank,
            holder_paid_b="0",
            holder_paid_units=0,
            min_cost_b="1",
            min_cost_units=1000,
            resulting_rank=1,
        )

    # Base query for active entries
    base_q = (
        select(BoardEntry)
        .where(BoardEntry.board_id == board.id, BoardEntry.status == "active")
        .join(BoardEntry.listing)
    )
    if category and category != "all":
        base_q = base_q.join(Listing.category).where(Category.slug == category)

    entries_result = await db.execute(
        base_q.order_by(BoardEntry.paid_units.desc(), BoardEntry.entered_at.asc())
    )
    entries = list(entries_result.scalars())

    # Determine holder's paid_units
    if target_rank <= len(entries):
        holder_entry = entries[target_rank - 1]
        holder_paid = holder_entry.paid_units
        min_cost = holder_paid + 1000  # +1 B
    else:
        # Claiming a new last place or empty slot
        holder_paid = 0
        min_cost = 1000  # floor 1 B

    # Resulting rank if paying min_cost
    resulting_rank = 1 + sum(1 for e in entries if e.paid_units >= min_cost)

    return QuoteOut(
        board_id=board.id,
        target_rank=target_rank,
        holder_paid_b=units_to_b_display(holder_paid),
        holder_paid_units=holder_paid,
        min_cost_b=units_to_b_display(min_cost),
        min_cost_units=min_cost,
        resulting_rank=resulting_rank,
    )


class ClaimRequest(BaseModel):
    listing_id: uuid.UUID
    period_type: str = "all_time"
    target_rank: int = 1
    paid_b: int = 1
    category: str | None = None


@router.post("/claim")
async def claim_rank(
    req: ClaimRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Claim a rank on the board with B coin."""
    # 1. Verify listing belongs to current user
    listing_result = await db.execute(
        select(Listing).where(
            Listing.id == req.listing_id,
            Listing.owner_id == current_user.id,
            Listing.deleted_at.is_(None),
        )
    )
    listing = listing_result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Kanal topilmadi yoki sizga tegishli emas")

    # 2. Get or create active board
    ref = now_tashkent()
    starts_at, ends_at, period_key = get_period_bounds(req.period_type, ref)
    board_result = await db.execute(
        select(Board).where(
            Board.period_type == req.period_type,
            Board.period_key == period_key,
            Board.status == "active",
        )
    )
    board = board_result.scalar_one_or_none()
    if not board:
        board = Board(
            period_type=req.period_type,
            period_key=period_key,
            starts_at=starts_at,
            ends_at=ends_at,
            status="active",
        )
        db.add(board)
        await db.flush()

    # 3. Check active entries on this board to compute exact price
    base_q = (
        select(BoardEntry)
        .where(BoardEntry.board_id == board.id, BoardEntry.status == "active")
        .join(BoardEntry.listing)
    )
    if req.category and req.category != "all":
        base_q = base_q.join(Listing.category).where(Category.slug == req.category)

    entries_result = await db.execute(
        base_q.order_by(BoardEntry.paid_units.desc(), BoardEntry.entered_at.asc())
    )
    active_entries = list(entries_result.scalars())

    if req.target_rank <= len(active_entries):
        holder = active_entries[req.target_rank - 1]
        min_cost = holder.paid_units + 1000
    else:
        min_cost = 1000

    min_cost_b = min_cost // 1000
    if req.paid_b < min_cost_b:
        raise HTTPException(
            status_code=400,
            detail=f"Ushbu #{req.target_rank}-o'rin uchun kamida {min_cost_b} B to'lash kerak"
        )

    charge_b = req.paid_b
    if current_user.balance < charge_b:
        raise HTTPException(
            status_code=400,
            detail=f"Mablag' yetarli emas. Balansingizda kamida {charge_b} B bo'lishi kerak"
        )

    # 4. Soft-replace old active entry for this listing on this board
    for e in active_entries:
        if e.listing_id == listing.id:
            e.status = "replaced"

    # 5. Deduct user balance
    current_user.balance -= charge_b

    # 6. Create new BoardEntry
    new_entry = BoardEntry(
        board_id=board.id,
        listing_id=listing.id,
        paid_units=charge_b * 1000,
        entered_at=now_tashkent(),
        status="active",
    )
    db.add(new_entry)
    await db.flush()

    # 7. Record in append-only ledger_entries
    ledger_entry = LedgerEntry(
        user_id=current_user.id,
        delta_units=-charge_b,
        kind="claim_rank",
        ref_type="board_entry",
        ref_id=str(new_entry.id),
        balance_after=current_user.balance,
    )
    db.add(ledger_entry)

    await db.commit()
    await db.refresh(new_entry)

    return {
        "success": True,
        "entry_id": str(new_entry.id),
        "paid_b": charge_b,
        "charge_b": charge_b,
        "new_balance": current_user.balance,
        "message": f"Kanal muvaffaqiyatli #{req.target_rank}-o'ringa joylashtirildi!"
    }

