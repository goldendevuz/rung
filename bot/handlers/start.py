"""Bot /start handler."""
from __future__ import annotations
import os
import redis.asyncio as redis
from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

router = Router()
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'), decode_responses=True)

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject) -> None:
    if command.args and command.args.startswith("login_"):
        token = command.args[6:]
        key = f"auth:tg:{token}"
        status = await redis_client.get(key)
        
        if not status or status != "pending":
            await message.answer("Ushbu havola yaroqsiz yoki muddati o'tgan.")
            return
            
        await redis_client.set(key, f"confirmed:{message.from_user.id}", ex=300)
        await message.answer("Kirish tasdiqlandi, saytga qaytishingiz mumkin")
        return

    await message.answer(
        "Salom! Men <b>Rung</b> botiman.\n\nBir pog'ona yuqoriga. \U0001FA9C"
    )
