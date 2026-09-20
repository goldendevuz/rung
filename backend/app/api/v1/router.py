"""API v1 router aggregator."""
from fastapi import APIRouter

from app.api.v1.routes.ping import router as ping_router
from app.api.v1.routes.boards import router as boards_router
from app.api.v1.routes.categories import router as categories_router
from app.api.v1.routes.listings import router as listings_router
from app.api.v1.routes.stats import router as stats_router

router = APIRouter()
router.include_router(ping_router)
router.include_router(boards_router)
router.include_router(categories_router)
router.include_router(listings_router)
router.include_router(stats_router)
