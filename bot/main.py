"""Rung Telegram bot entry point."""
from __future__ import annotations
import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)
HEARTBEAT = Path('/tmp/bot_heartbeat')


async def heartbeat_loop() -> None:
    while True:
        HEARTBEAT.touch()
        await asyncio.sleep(10)


async def main() -> None:
    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', 'INFO').upper(),
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
    )

    env = os.getenv('ENV', 'dev')
    if env == 'dev':
        bot_token = os.getenv('BOT_TOKEN_DEV', os.getenv('BOT_TOKEN', '')).strip()
    else:
        bot_token = os.getenv('BOT_TOKEN', '').strip()

    if not bot_token:
        logger.warning('BOT_TOKEN is not set - bot idle')
        asyncio.create_task(heartbeat_loop())
        await asyncio.Event().wait()
        return

    from aiogram import Bot, Dispatcher
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from handlers.start import router as start_router
    from handlers.admin import router as admin_router
    from handlers.tracking import router as tracking_router

    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(tracking_router)

    try:
        me = await bot.get_me()
        logger.info('Bot started: id=%s username=@%s', me.id, me.username)
    except Exception as exc:
        logger.error('getMe failed: %s', exc)
        raise

    asyncio.create_task(heartbeat_loop())
    await dp.start_polling(bot, allowed_updates=["message", "chat_member", "my_chat_member"])


if __name__ == '__main__':
    asyncio.run(main())
