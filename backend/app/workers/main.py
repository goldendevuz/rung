"""arq worker entry point — S0 skeleton."""
from __future__ import annotations
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
HEARTBEAT = Path('/tmp/worker_heartbeat')


async def _heartbeat_loop() -> None:
    while True:
        HEARTBEAT.touch()
        await asyncio.sleep(10)


async def startup(ctx: dict) -> None:  # type: ignore[type-arg]
    logger.info('Worker starting')
    HEARTBEAT.touch()


async def shutdown(ctx: dict) -> None:  # type: ignore[type-arg]
    logger.info('Worker shutting down')


class WorkerSettings:
    functions: list = []  # type: ignore[type-arg]
    on_startup = startup
    on_shutdown = shutdown


if __name__ == '__main__':
    import arq
    from app.core.config import get_settings

    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    loop = asyncio.get_event_loop()
    loop.create_task(_heartbeat_loop())

    arq.run_worker(  # type: ignore[attr-defined]
        WorkerSettings,
        redis_settings=arq.connections.RedisSettings.from_dsn(settings.REDIS_URL),  # type: ignore[attr-defined]
    )
