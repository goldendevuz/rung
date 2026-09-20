"""arq worker entry point — S0 skeleton."""
from __future__ import annotations
import asyncio
import logging
from pathlib import Path

import arq

logger = logging.getLogger(__name__)
HEARTBEAT = Path('/tmp/worker_heartbeat')


async def noop(ctx: dict) -> str:  # type: ignore[type-arg]
    """Placeholder task — keeps arq happy in S0."""
    HEARTBEAT.touch()
    logger.debug('noop task ran')
    return 'ok'


async def startup(ctx: dict) -> None:  # type: ignore[type-arg]
    logger.info('Worker starting')
    HEARTBEAT.touch()


async def shutdown(ctx: dict) -> None:  # type: ignore[type-arg]
    logger.info('Worker shutting down')


class WorkerSettings:
    functions = [noop]
    on_startup = startup
    on_shutdown = shutdown
    # Write heartbeat on every job completion
    after_job_end = None


if __name__ == '__main__':
    import os
    from app.core.config import get_settings

    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    arq.run_worker(
        WorkerSettings,
        redis_settings=arq.connections.RedisSettings.from_dsn(settings.REDIS_URL),
    )
