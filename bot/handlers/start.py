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
            
        import json
        user_data = {
            "tg_id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "username": message.from_user.username
        }
        await redis_client.set(key, f"confirmed:{json.dumps(user_data)}", ex=300)
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        webapp_url = os.getenv('WEBAPP_URL', 'https://rung.uz')
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Saytga qaytish", url=webapp_url)]
        ])
        await message.answer("Kirish tasdiqlandi, saytga qaytishingiz mumkin", reply_markup=kb)
        return

    await message.answer(
        "Salom! Men <b>Rung</b> botiman.\n\nBir pog'ona yuqoriga. \U0001FA9C"
    )
