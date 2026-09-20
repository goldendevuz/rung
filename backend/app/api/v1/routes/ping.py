"""Ping endpoint for smoke tests."""
from fastapi import APIRouter

router = APIRouter(tags=['ping'])


@router.get('/ping')
async def ping() -> dict[str, str]:
    return {'pong': 'rung'}
