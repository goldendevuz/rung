"""FastAPI application entry point."""
from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1.router import router as api_v1_router

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info('Rung backend starting (ENV=%s)', settings.ENV)
    if settings.SEED_DEMO:
        logger.info('SEED_DEMO=true — running demo seed')
        try:
            from app.db.seed import run_seed
            await run_seed()
            logger.info('Demo seed complete')
        except Exception:
            logger.exception('Seed failed — continuing startup anyway')
    yield
    logger.info('Rung backend shutting down')


app = FastAPI(
    title='Rung API',
    version='0.1.0',
    docs_url='/api/v1/docs',
    redoc_url='/api/v1/redoc',
    openapi_url='/api/v1/openapi.json',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz', tags=['health'])
async def healthz() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/readyz', tags=['health'])
async def readyz() -> dict[str, str]:
    return {'status': 'ok'}


app.include_router(api_v1_router, prefix='/api/v1')
