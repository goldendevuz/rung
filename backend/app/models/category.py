"""Category model."""
from __future__ import annotations

from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin, SoftDeleteMixin, TimestampMixin


class Category(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"

    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name_uz: Mapped[str] = mapped_column(String(80), nullable=False)
    color: Mapped[str] = mapped_column(String(32), nullable=False, default="#7C6CFF")
    icon: Mapped[str | None] = mapped_column(String(8), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    listings: Mapped[list["Listing"]] = relationship(  # noqa: F821
        "Listing", back_populates="category", lazy="noload"
    )
