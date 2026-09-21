"""Board and BoardEntry models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin, SoftDeleteMixin, TimestampMixin


class Board(Base, IDMixin, TimestampMixin):
    __tablename__ = "boards"

    # period_type: all_time | daily | weekly | monthly | seasonal | yearly
    period_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    # period_key: e.g. "2026-09-20" for daily, "2026-W38" for weekly, "all_time" for all_time
    period_key: Mapped[str] = mapped_column(String(32), nullable=False)

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # active | closed
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)

    entries: Mapped[list["BoardEntry"]] = relationship(
        "BoardEntry", back_populates="board", lazy="noload"
    )

    __table_args__ = (
        UniqueConstraint("period_type", "period_key", name="uq_board_period"),
    )


class BoardEntry(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "board_entries"

    board_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    listing_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # paid_units: whole B * 1000; 0 for free catalog entries
    paid_units: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    # Timestamp when this entry was inserted (for tie-break)
    entered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )

    # active | replaced | cancelled
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)

    board: Mapped["Board"] = relationship("Board", back_populates="entries")
    listing: Mapped["Listing"] = relationship("Listing", back_populates="board_entries")

    __table_args__ = (
        # Only one active entry per listing per board
        Index(
            "ix_board_entries_active_listing",
            "board_id",
            "listing_id",
            unique=True,
            postgresql_where="status = 'active'",
        ),
        # Fast rank derivation
        Index(
            "ix_board_entries_rank",
            "board_id",
            "paid_units",
            "entered_at",
            postgresql_where="status = 'active'",
        ),
    )
