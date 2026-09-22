"""Application configuration via pydantic-settings."""
from __future__ import annotations
import sys
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    ENV: str = 'dev'
    TZ: str = 'Asia/Tashkent'
    LOG_LEVEL: str = 'INFO'

    DATABASE_URL: str = 'postgresql+asyncpg://rung:rung@postgres:5432/rung'
    POSTGRES_USER: str = 'rung'
    POSTGRES_PASSWORD: str = ''
    POSTGRES_DB: str = 'rung'

    REDIS_URL: str = 'redis://redis:6379/0'

    SECRET_KEY: str = 'changeme'
    INTERNAL_API_TOKEN: str = 'changeme'

    BOT_TOKEN: str = ''
    BOT_USERNAME: str = 'rung_uz_bot'
    ADMIN_TG_IDS: str = ''

    WEBAPP_URL: str = 'http://localhost'
    PUBLIC_BASE_URL: str = 'http://localhost'
    CORS_ORIGINS: str = 'http://localhost'

    GOOGLE_CLIENT_ID: str = ''
    GOOGLE_CLIENT_SECRET: str = ''

    DEV_AUTH: bool = False
    SEED_DEMO: bool = False
    STARS_ENABLED: bool = False
    PAYNET_ENABLED: bool = False
    GOOGLE_AUTH_ENABLED: bool = False
    SHOW_DEMO_BUTTON: bool = False
    PAYMENT_PROVIDER_TEXT: str = "avtomatik to'lov: Click, Payme (inPAY)"
    SHOW_PAYMENT_DETAILS: bool = False
    SHOW_LIVE_STATS: bool = True
    ENABLED_LISTING_KINDS: str = 'channel'

    INPAY_MERCHANT_ID: str = ''
    INPAY_MERCHANT_TOKEN: str = ''
    INPAY_CALLBACK_URL: str = 'https://rung.shats.uz/api/v1/payments/inpay/callback'
    INPAY_RETURN_URL: str = 'https://rung.shats.uz/hamyon'
    INPAY_BASE_URL: str = 'https://inpay.uz/api/v1'

    B_UNIT_UZS: int = 1000
    STARS_UNITS_PER_STAR: int = 200
    FLOOR_B: int = 1
    MIN_STEP_B: int = 1
    MANUAL_MIN_UZS: int = 1000
    MANUAL_STEP_UZS: int = 1000

    @model_validator(mode='after')
    def check_prod_dev_auth(self) -> 'Settings':
        if self.ENV == 'prod' and self.DEV_AUTH:
            print('FATAL: DEV_AUTH=true is not allowed in prod', file=sys.stderr)
            sys.exit(1)
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(',') if o.strip()]

    @property
    def admin_tg_ids_set(self) -> set[int]:
        return {int(i.strip()) for i in self.ADMIN_TG_IDS.split(',') if i.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
