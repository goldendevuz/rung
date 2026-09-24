from __future__ import annotations
import uuid
from sqlalchemy import BigInteger, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin, TimestampMixin


class SubscriberEvent(Base, IDMixin, TimestampMixin):
    __tablename__ = "subscriber_events"

    # Foreign Key to Listing
    listing_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("listings.id", ondelete="CASCADE"), nullable=True, index=True
    )
    listing: Mapped["Listing"] = relationship("Listing")  # noqa: F821

    # Event details
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    
    action: Mapped[str] = mapped_column(String(32), nullable=False) # 'join' or 'leave'
    source: Mapped[str] = mapped_column(String(32), nullable=False) # 'group' or 'channel'

    # Note: `created_at` from TimestampMixin serves as `occurred_at`.
