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
import uuid
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.public import (
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


@router.get("/{board_id}/quote", response_model=QuoteOut)
async def get_quote(
    board_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    target_rank: int = Query(..., ge=1),
) -> QuoteOut:
    """Read-only quote: cost to claim target_rank on a board."""
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if board is None or board.status != "active":
        raise HTTPException(status_code=404, detail="Board not found or not active")

    # Get all active entries ranked
    entries_result = await db.execute(
        select(BoardEntry)
        .where(BoardEntry.board_id == board.id, BoardEntry.status == "active")
        .order_by(BoardEntry.paid_units.desc(), BoardEntry.entered_at.asc())
    )
    entries = list(entries_result.scalars())

    # Determine holder's paid_units
    if target_rank <= len(entries):
        holder_entry = entries[target_rank - 1]
        holder_paid = holder_entry.paid_units
        min_cost = holder_paid + 1000  # +1 B
    else:
        # Claiming a new last place or beyond
        holder_paid = 0
        min_cost = 1000  # floor 1 B

    # Resulting rank if paying min_cost
    resulting_rank = 1 + sum(1 for e in entries if e.paid_units >= min_cost)

    return QuoteOut(
        board_id=board_id,
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

    # 2. Check balance
    if current_user.balance < req.paid_b:
        raise HTTPException(status_code=400, detail="Mablag' yetarli emas. Balansingizda kamida 1 B bo'lishi kerak")

    # 3. Get or create active board
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

    # 4. Check active entries on this board
    entries_result = await db.execute(
        select(BoardEntry)
        .where(BoardEntry.board_id == board.id, BoardEntry.status == "active")
        .order_by(BoardEntry.paid_units.desc(), BoardEntry.entered_at.asc())
    )
    active_entries = list(entries_result.scalars())

    paid_units = req.paid_b * 1000
    if req.target_rank <= len(active_entries):
        holder = active_entries[req.target_rank - 1]
        min_cost = holder.paid_units + 1000
    else:
        min_cost = 1000

    if paid_units < min_cost:
        raise HTTPException(status_code=400, detail=f"Ushbu o'rin uchun kamida {min_cost // 1000} B to'lash kerak")

    # 5. Soft-replace old active entry for this listing on this board
    for e in active_entries:
        if e.listing_id == listing.id:
            e.status = "replaced"

    # 6. Deduct user balance
    current_user.balance -= req.paid_b

    # 7. Create new BoardEntry
    new_entry = BoardEntry(
        board_id=board.id,
        listing_id=listing.id,
        paid_units=paid_units,
        entered_at=now_tashkent(),
        status="active",
    )
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)

    return {
        "success": True,
        "entry_id": str(new_entry.id),
        "paid_b": req.paid_b,
        "new_balance": current_user.balance,
        "message": f"Kanal muvaffaqiyatli #{req.target_rank}-o'ringa joylashtirildi!"
    }

