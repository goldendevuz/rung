"""API v1 router aggregator."""
from fastapi import APIRouter
from app.api.v1.routes.ping import router as ping_router

router = APIRouter()
router.include_router(ping_router)
