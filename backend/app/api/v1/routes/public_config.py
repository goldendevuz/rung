"""Public configuration endpoint — used by the frontend to discover feature flags.

Returns only information that is safe to expose publicly.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(prefix="/public-config", tags=["config"])

settings = get_settings()


class PublicConfig(BaseModel):
    show_demo_button: bool
    google_auth_enabled: bool
    stars_enabled: bool
    paynet_enabled: bool
    payment_provider_text: str


@router.get("", response_model=PublicConfig)
async def get_public_config() -> PublicConfig:
    """Return feature flags and copy that the frontend reads at runtime."""
    return PublicConfig(
        show_demo_button=settings.SHOW_DEMO_BUTTON,
        google_auth_enabled=settings.GOOGLE_AUTH_ENABLED,
        stars_enabled=settings.STARS_ENABLED,
        paynet_enabled=settings.PAYNET_ENABLED,
        payment_provider_text=settings.PAYMENT_PROVIDER_TEXT,
    )
