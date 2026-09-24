from __future__ import annotations
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.topup import TopupOrder
from app.models.user import User
from app.services.inpay import create_inpay_order, InPayError
from app.core.rate_limit import rate_limit

router = APIRouter(prefix="/wallet", tags=["wallet"])
settings = get_settings()


class TopupRequest(BaseModel):
    b_amount: int = Field(..., ge=1, description="Top-up amount in whole B coins (minimum 1 B)")


class TopupResponse(BaseModel):
    pay_url: str
    order_id: str


class TopupStatusResponse(BaseModel):
    order_id: str
    b_amount: int
    amount_uzs: int
    status: str
    created_at: str


@router.post(
    "/topup",
    response_model=TopupResponse,
    dependencies=[Depends(rate_limit("wallet_topup", limit=5, window_seconds=60))]
)
async def create_topup(
    req: TopupRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request,
) -> TopupResponse:
    """
    Initiate an automatic UZS wallet top-up via inPAY.uz.
    Converts whole B to UZS, requests inPAY hosted checkout,
    and returns pay_url and order_id.
    Captures datafast_visitor_id cookie for server-side attribution.
    """
    if req.b_amount < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimal to'ldirish miqdori 1 B",
        )

    amount_uzs = req.b_amount * settings.B_UNIT_UZS
    description = f"Rung hamyonini to'ldirish: {req.b_amount} B ({amount_uzs:,} so'm)"

    try:
        order_id, pay_url = await create_inpay_order(
            amount_uzs=amount_uzs,
            description=description,
        )
    except InPayError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"To'lov tizimiga ulanishda xatolik: {str(e)}",
        )

    # Capture datafast_visitor_id cookie
    datafast_visitor_id = request.cookies.get("datafast_visitor_id")

    # Store pending top-up row keyed by inPAY order_id
    topup_order = TopupOrder(
        user_id=current_user.id,
        order_id=order_id,
        b_amount=req.b_amount,
        amount_uzs=amount_uzs,
        status="pending",
        pay_url=pay_url,
        datafast_visitor_id=datafast_visitor_id,
    )
    db.add(topup_order)
    await db.commit()

    return TopupResponse(
        pay_url=pay_url,
        order_id=order_id,
    )


@router.get("/topup/{order_id}", response_model=TopupStatusResponse)
async def get_topup_status(
    order_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TopupStatusResponse:
    """
    Poll the status of a top-up from OUR database.
    Returns pending, completed, or failed.
    """
    stmt = select(TopupOrder).where(TopupOrder.order_id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyurtma topilmadi",
        )

    return TopupStatusResponse(
        order_id=order.order_id,
        b_amount=order.b_amount,
        amount_uzs=order.amount_uzs,
        status=order.status,
        created_at=order.created_at.isoformat(),
    )


class TransactionItem(BaseModel):
    id: str
    created_at: str
    kind: str
    delta_b: int
    balance_after_b: int
    description: str


class HistoryResponse(BaseModel):
    items: list[TransactionItem]
    total: int
    page: int
    page_size: int


@router.get("/history", response_model=HistoryResponse)
async def get_wallet_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 20,
) -> HistoryResponse:
    """Return paginated ledger history for the current user, most recent first."""
    from sqlalchemy import desc
    from app.models.board import BoardEntry
    from app.models.listing import Listing
    from app.models.ledger import LedgerEntry

    offset = (page - 1) * page_size

    count_stmt = select(func.count(LedgerEntry.id)).where(LedgerEntry.user_id == current_user.id)
    total = (await db.execute(count_stmt)).scalar_one() or 0

    stmt = (
        select(LedgerEntry)
        .where(LedgerEntry.user_id == current_user.id)
        .order_by(desc(LedgerEntry.created_at))
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()

    items: list[TransactionItem] = []
    for e in entries:
        description = ""
        if e.kind == "topup_inpay_uz":
            description = "Hamyon to\'ldirildi: +{} B".format(e.delta_units)
        elif e.kind == "claim_rank":
            listing_name = None
            try:
                from uuid import UUID
                be_id = UUID(e.ref_id)
                be_result = await db.execute(
                    select(BoardEntry).where(BoardEntry.id == be_id)
                )
                be = be_result.scalar_one_or_none()
                if be:
                    l_result = await db.execute(
                        select(Listing).where(Listing.id == be.listing_id)
                    )
                    lst = l_result.scalar_one_or_none()
                    if lst:
                        listing_name = lst.name
            except Exception:
                pass
            if listing_name:
                description = "O\'rin uchun to\'landi: {}".format(listing_name)
            else:
                description = "O\'rin uchun to\'landi"
        else:
            description = e.kind

        items.append(TransactionItem(
            id=str(e.id),
            created_at=e.created_at.isoformat(),
            kind=e.kind,
            delta_b=e.delta_units,
            balance_after_b=e.balance_after,
            description=description,
        ))

    return HistoryResponse(items=items, total=total, page=page, page_size=page_size)
