"""Models package — import all so Alembic can discover them."""
from app.models.category import Category
from app.models.listing import Listing
from app.models.board import Board, BoardEntry
from app.models.stats import ListingStatsDaily
from app.models.setting import Setting

__all__ = [
    "Category",
    "Listing",
    "Board",
    "BoardEntry",
    "ListingStatsDaily",
    "Setting",
]
