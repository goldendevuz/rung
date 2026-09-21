"""ListingStatsDaily model — daily click-through rollups."""
from __future__ import annotations

from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Index, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin, TimestampMixin


class ListingStatsDaily(Base, IDMixin, TimestampMixin):
    __tablename__ = "listing_stats_daily"

    listing_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stat_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Verified unique click-throughs for that day
    clickthroughs: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)

    listing: Mapped["Listing"] = relationship("Listing", back_populates="stats_daily")  # noqa: F821

    __table_args__ = (
        UniqueConstraint("listing_id", "stat_date", name="uq_stats_listing_date"),
    )
