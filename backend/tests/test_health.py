"""Smoke test: healthz and ping endpoints."""
from __future__ import annotations
import os
import pytest
from httpx import AsyncClient, ASGITransport

os.environ.setdefault('DATABASE_URL', 'postgresql+asyncpg://rung:rung@localhost:5432/rung')
os.environ.setdefault('SECRET_KEY', 'testsecretkey000000000000000000000000000000000000000000000000')
os.environ.setdefault('INTERNAL_API_TOKEN', 'testtoken')

from app.main import app


@pytest.mark.asyncio
async def test_healthz() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        resp = await ac.get('/healthz')
    assert resp.status_code == 200
    assert resp.json()['status'] == 'ok'


@pytest.mark.asyncio
async def test_ping() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        resp = await ac.get('/api/v1/ping')
    assert resp.status_code == 200
    assert resp.json()['pong'] == 'rung'
