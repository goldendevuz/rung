"""API v1 router aggregator."""
from fastapi import APIRouter

from app.api.v1.routes.ping import router as ping_router
from app.api.v1.routes.boards import router as boards_router
from app.api.v1.routes.categories import router as categories_router
from app.api.v1.routes.listings import router as listings_router
from app.api.v1.routes.stats import router as stats_router
from app.api.v1.routes.public_config import router as public_config_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.wallet import router as wallet_router
from app.api.v1.routes.payments import router as payments_router

router = APIRouter()
router.include_router(ping_router)
router.include_router(boards_router)
router.include_router(categories_router)
router.include_router(listings_router)
router.include_router(stats_router)
router.include_router(public_config_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(wallet_router)
router.include_router(payments_router)
