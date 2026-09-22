from __future__ import annotations
import uuid
from typing import Optional
from sqlalchemy import BigInteger, String, Uuid, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin, TimestampMixin


class TopupOrder(Base, IDMixin, TimestampMixin):
    __tablename__ = "topup_orders"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    b_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount_uzs: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    pay_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    user: Mapped["User"] = relationship("User")  # noqa: F821
