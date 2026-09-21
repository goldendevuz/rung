"""FastAPI application entry point."""
from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.v1.router import router as api_v1_router
from app.demo.fixtures import (
    get_demo_categories,
    get_demo_stats,
    get_demo_tabs,
    get_demo_board_current,
    get_demo_daily_history,
)

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info('Rung backend starting (ENV=%s)', settings.ENV)
    try:
        from app.db.seed import seed_reference
        await seed_reference()
        logger.info('Reference seed complete')
    except Exception:
        logger.exception('Reference seed failed — continuing startup anyway')
    if settings.SEED_DEMO:
        logger.info('SEED_DEMO=true — running demo seed')
        try:
            from app.db.seed import seed_demo
            await seed_demo()
            logger.info('Demo seed complete')
        except Exception:
            logger.exception('Demo seed failed — continuing startup anyway')
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

@app.middleware("http")
async def demo_mode_middleware(request: Request, call_next):
    if request.headers.get("x-rung-demo") == "1":
        if request.method not in ["GET", "OPTIONS"]:
            return JSONResponse(status_code=403, content={"detail": "Demo rejimida ruxsat etilmagan"})
            
        path = request.url.path
        if path == "/api/v1/categories":
            return JSONResponse(content=get_demo_categories())
        elif path == "/api/v1/stats/public":
            return JSONResponse(content=get_demo_stats())
        elif path == "/api/v1/boards/tabs":
            return JSONResponse(content=get_demo_tabs())
        elif path == "/api/v1/boards/daily/history":
            return JSONResponse(content=get_demo_daily_history())
        elif path.startswith("/api/v1/boards/") and path.endswith("/current"):
            period_type = path.split("/")[-2]
            page = int(request.query_params.get("page", 1))
            category = request.query_params.get("category")
            q = request.query_params.get("q")
            return JSONResponse(content=get_demo_board_current(period_type, page, category, q))
        elif "/api/v1/listings/" in path:
            if "_kodlash_uz_" in path:
                return JSONResponse(content={
                    "public_id": "_kodlash_uz_",
                    "handle": "@kodlash_uz",
                    "name": "Kodlash.uz",
                    "description": "O'zbekistondagi eng yirik dasturlash kanali. Bizning kanalda siz dasturlash sirlarini organishingiz, python, javascript, va boshqa dasturlash tillari boyicha darslarni kuzatib borishingiz mumkin. Har kuni yangi malumotlar va qiziqarli maqolalar chop etiladi. Shuningdek, bizning obunachilarimiz orasida tajribali mutaxassislar ham mavjud bo'lib, ular sizga maslahatlar berishadi. Bu O'zbekistonning eng katta IT hamjamiyati bo'lib, bu yerda o'rganish, ishlash va rivojlanish uchun barcha imkoniyatlar mavjud. Biz bilan birga bo'ling va o'z bilimingizni oshiring!",
                    "category_slug": "dasturlash",
                    "category_color": "#2563EB",
                    "subscribers": 84200,
                    "verified": True,
                    "claimed": True,
                    "free_label": None,
                    "gradient_start": "#2563EB",
                    "gradient_end": "#1E3A8A",
                    "clickthroughs": 1289,
                    "created_at": "2026-05-24T08:08:05.033794Z",
                    "status": "active"
                })
            elif "yoq-bunday-kanal" in path:
                return JSONResponse(status_code=404, content={"detail": "Not Found"})
        elif path.startswith("/api/v1/boards/") and path.endswith("/quote"):
            # Mock quote for demo
            board_id = path.split("/")[-2]
            target_rank = int(request.query_params.get("target_rank", 1))
            return JSONResponse(content={
                "board_id": board_id,
                "target_rank": target_rank,
                "holder_paid_b": "49",
                "holder_paid_units": 49000,
                "min_cost_b": "50",
                "min_cost_units": 50000,
                "resulting_rank": target_rank,
            })
            
    response = await call_next(request)
    return response


@app.get('/healthz', tags=['health'])
async def healthz() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/readyz', tags=['health'])
async def readyz() -> dict[str, str]:
    return {'status': 'ok'}


app.include_router(api_v1_router, prefix='/api/v1')
