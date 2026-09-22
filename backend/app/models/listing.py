from __future__ import annotations
import uuid
"""Listing model."""

from sqlalchemy import Uuid, ARRAY, BigInteger, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin, SoftDeleteMixin, TimestampMixin



class Listing(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "listings"

    # Identity
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="channel")

    # Content
    handle: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Category FK
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category: Mapped["Category"] = relationship("Category", back_populates="listings")  # noqa: F821

    # Ownership
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    owner: Mapped["User"] = relationship("User")  # noqa: F821

    # Channel-specific
    subscribers: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    claimed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Status: active | hidden
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)

    # Free catalog label (e.g. "Rung jamoasi", "Egasi tasdiqlanmagan")
    free_label: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Logo URL (uploaded or fetched)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Avatar gradient colors [color1, color2]
    gradient_start: Mapped[str] = mapped_column(String(32), nullable=False, default="#7C6CFF")
    gradient_end: Mapped[str] = mapped_column(String(32), nullable=False, default="#3A4147")

    # Relationships
    board_entries: Mapped[list["BoardEntry"]] = relationship(  # noqa: F821
        "BoardEntry", back_populates="listing", lazy="noload"
    )
    stats_daily: Mapped[list["ListingStatsDaily"]] = relationship(  # noqa: F821
        "ListingStatsDaily", back_populates="listing", lazy="noload"
    )
