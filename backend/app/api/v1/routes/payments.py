from __future__ import annotations
import logging
from typing import Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.ledger import LedgerEntry
from app.models.topup import TopupOrder
from app.models.user import User
from app.services.inpay import verify_inpay_transaction, InPayError

router = APIRouter(prefix="/payments", tags=["payments"])
logger = logging.getLogger(__name__)


class InPayCallbackPayload(BaseModel):
    amount: Any = None
    status: Any = None
    order_id: Any = None
    transaction_id: Any = None
    created_at: Any = None


@router.post("/inpay/callback", status_code=status.HTTP_200_OK)
async def inpay_webhook_callback(
    payload: InPayCallbackPayload,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    inPAY webhook callback handler.
    IMPORTANT: This payload is NOT trusted on its own (no signature).
    We ALWAYS respond HTTP 200 to satisfy inPAY's retry mechanism.
    We independently call GET /api/v1/transactions/?order_id= to verify
    the transaction status and amount before crediting the wallet.
    A DB-level unique constraint on order_id in ledger_entries guarantees idempotency.
    """
    raw_order_id = payload.order_id
    if not raw_order_id:
        logger.warning("inPAY webhook received without order_id: %s", payload)
        return {"status": "ok"}

    order_id = str(raw_order_id).strip()

    # 1. Look up the pending top-up order
    stmt = select(TopupOrder).where(TopupOrder.order_id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        logger.warning("inPAY webhook received for unknown order_id: %s", order_id)
        return {"status": "ok"}

    if order.status == "completed":
        logger.info("inPAY webhook received for already completed order_id: %s", order_id)
        return {"status": "ok"}

    # 2. Server-to-server verification with inPAY API
    try:
        verified = await verify_inpay_transaction(order_id)
    except InPayError as e:
        logger.error("inPAY verification failed for order_id %s: %s", order_id, e)
        return {"status": "ok"}

    v_status = str(verified.get("status", "")).lower()
    v_amount = verified.get("amount")
    v_tx_id = verified.get("transaction_id") or str(payload.transaction_id or "")

    logger.info(
        "inPAY server verification result for %s: status=%s, amount=%s (expected=%s)",
        order_id,
        v_status,
        v_amount,
        order.amount_uzs,
    )

    # 3. Only credit if status is success and amount matches expected UZS
    if v_status == "success" and v_amount == order.amount_uzs:
        # Lock user row to prevent race conditions
        user_stmt = select(User).where(User.id == order.user_id).with_for_update()
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error("User %s not found for order %s", order.user_id, order_id)
            return {"status": "ok"}

        # Double check idempotency in ledger
        ledger_stmt = select(LedgerEntry).where(LedgerEntry.ref_id == order_id)
        existing_ledger = (await db.execute(ledger_stmt)).scalar_one_or_none()

        if existing_ledger:
            logger.warning("Ledger entry already exists for order_id %s, skipping credit", order_id)
            order.status = "completed"
            await db.commit()
            return {"status": "ok"}

        # Credit wallet and record in ledger
        user.balance += order.b_amount

        ledger_entry = LedgerEntry(
            user_id=user.id,
            delta_units=order.b_amount,
            kind="topup_inpay_uz",
            ref_type="inpay_order",
            ref_id=order_id,
            balance_after=user.balance,
        )
        db.add(ledger_entry)

        order.status = "completed"
        order.transaction_id = v_tx_id
        await db.commit()
        logger.info(
            "Successfully credited %s B to user %s for order %s (new balance: %s B)",
            order.b_amount,
            user.id,
            order_id,
            user.balance,
        )
    elif v_status in ["failed", "canceled", "cancelled", "rejected"]:
        order.status = "failed"
        order.transaction_id = v_tx_id
        await db.commit()
        logger.info("Marked order %s as failed (inPAY status: %s)", order_id, v_status)

    return {"status": "ok"}
