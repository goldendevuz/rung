"""Bot /start handler."""
from __future__ import annotations
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Salom! Men <b>Rung</b> botiman.\n\nBir pog'ona yuqoriga. \U0001FA9C"
    )
