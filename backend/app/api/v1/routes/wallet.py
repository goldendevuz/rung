from __future__ import annotations
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.topup import TopupOrder
from app.models.user import User
from app.services.inpay import create_inpay_order, InPayError

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


@router.post("/topup", response_model=TopupResponse)
async def create_topup(
    req: TopupRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TopupResponse:
    """
    Initiate an automatic UZS wallet top-up via inPAY.uz.
    Converts whole B to UZS, requests inPAY hosted checkout,
    and returns pay_url and order_id.
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

    # Store pending top-up row keyed by inPAY order_id
    topup_order = TopupOrder(
        user_id=current_user.id,
        order_id=order_id,
        b_amount=req.b_amount,
        amount_uzs=amount_uzs,
        status="pending",
        pay_url=pay_url,
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
