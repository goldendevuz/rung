"""arq worker entry point."""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import arq
from arq import cron
from sqlalchemy import select

from app.db.session import async_session_factory
from app.models.board import Board, BoardEntry
from app.models.topup import TopupOrder
from app.models.user import User
from app.models.ledger import LedgerEntry
from app.services.inpay import verify_inpay_transaction, InPayError
from app.services.datafast import track_datafast_payment

logger = logging.getLogger(__name__)
HEARTBEAT = Path('/tmp/worker_heartbeat')


async def noop(ctx: dict) -> str:  # type: ignore[type-arg]
    """Placeholder task — keeps arq happy in S0."""
    HEARTBEAT.touch()
    logger.debug('noop task ran')
    return 'ok'


async def reconcile_inpay_topups(ctx: dict) -> int:  # type: ignore[type-arg]
    """
    Reconciliation job (arq, every 1 minute):
    Find top-up rows still pending for more than ~2 minutes,
    call GET /transactions/?order_id= for each, and apply credit-only-after-server-check.
    """
    HEARTBEAT.touch()
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=2)
    reconciled_count = 0

    async with async_session_factory() as db:
        stmt = (
            select(TopupOrder)
            .where(
                TopupOrder.status == "pending",
                TopupOrder.created_at <= cutoff,
            )
            .limit(50)
        )
        result = await db.execute(stmt)
        pending_orders = result.scalars().all()

        for order in pending_orders:
            try:
                verified = await verify_inpay_transaction(order.order_id)
            except InPayError as e:
                logger.warning("Reconciliation verify error for %s: %s", order.order_id, e)
                continue

            v_status = str(verified.get("status", "")).lower()
            v_amount = verified.get("amount")
            v_tx_id = verified.get("transaction_id") or ""

            if v_status == "success" and v_amount == order.amount_uzs:
                user_stmt = select(User).where(User.id == order.user_id).with_for_update()
                user = (await db.execute(user_stmt)).scalar_one_or_none()
                if not user:
                    continue

                ledger_stmt = select(LedgerEntry).where(LedgerEntry.ref_id == order.order_id)
                existing_ledger = (await db.execute(ledger_stmt)).scalar_one_or_none()
                if not existing_ledger:
                    user.balance += order.b_amount
                    ledger_entry = LedgerEntry(
                        user_id=user.id,
                        delta_units=order.b_amount,
                        kind="topup_inpay_uz",
                        ref_type="inpay_order",
                        ref_id=order.order_id,
                        balance_after=user.balance,
                    )
                    db.add(ledger_entry)

                order.status = "completed"
                order.transaction_id = v_tx_id
                await db.commit()
                reconciled_count += 1
                logger.info("Reconciliation credited %s B for order %s", order.b_amount, order.order_id)

                # Fire DataFast revenue tracking event (server-side, post-verification)
                await track_datafast_payment(
                    amount_uzs=order.amount_uzs,
                    order_id=order.order_id,
                    datafast_visitor_id=order.datafast_visitor_id,
                )

            elif v_status in ["failed", "canceled", "cancelled", "rejected"]:
                order.status = "failed"
                order.transaction_id = v_tx_id
                await db.commit()
                logger.info("Reconciliation marked order %s as failed", order.order_id)

    return reconciled_count



async def reset_daily_board(ctx: dict) -> dict:  # type: ignore[type-arg]
    """
    Daily board reset (arq cron, runs at UTC 19:00 = Tashkent 00:00).
    Closes the current daily board by marking all active entries as expired.
    The next claim on the daily period auto-creates a fresh board via get_period_bounds.
    """
    from sqlalchemy import update as sa_update
    from app.core.periods import now_tashkent, get_period_bounds

    HEARTBEAT.touch()
    ref = now_tashkent()
    _, _, period_key = get_period_bounds("daily", ref)

    async with async_session_factory() as db:
        result = await db.execute(
            select(Board).where(
                Board.period_type == "daily",
                Board.period_key == period_key,
                Board.status == "active",
            )
        )
        board = result.scalar_one_or_none()

        if board is None:
            logger.info("reset_daily_board: no active daily board for %s", period_key)
            return {"reset": False, "period_key": period_key}

        await db.execute(
            sa_update(BoardEntry)
            .where(BoardEntry.board_id == board.id, BoardEntry.status == "active")
            .values(status="expired")
        )
        board.status = "closed"
        await db.commit()

        logger.info("reset_daily_board: closed board %s (period_key=%s)", board.id, period_key)
        return {"reset": True, "board_id": str(board.id), "period_key": period_key}


async def startup(ctx: dict) -> None:  # type: ignore[type-arg]
    logger.info('Worker starting')
    HEARTBEAT.touch()


async def shutdown(ctx: dict) -> None:  # type: ignore[type-arg]
    logger.info('Worker shutting down')


class WorkerSettings:
    functions = [noop, reconcile_inpay_topups, reset_daily_board]
    cron_jobs = [
        cron(reconcile_inpay_topups, minute=None, second=0),
        cron(reset_daily_board, hour=19, minute=0, second=0),  # UTC 19:00 = Tashkent 00:00
    ]
    on_startup = startup
    on_shutdown = shutdown
    after_job_end = None


if __name__ == '__main__':
    import os
    from app.core.config import get_settings

    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    arq.run_worker(
        WorkerSettings,
        redis_settings=arq.connections.RedisSettings.from_dsn(settings.REDIS_URL),
    )
