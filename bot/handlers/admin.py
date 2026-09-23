from datetime import datetime, timezone, timedelta
import html
import logging
import os
from typing import Any

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
import httpx

logger = logging.getLogger(__name__)

router = Router()

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend_prod:8000").rstrip("/")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")


def format_tashkent_time(iso_str: str | None) -> str:
    """Format ISO UTC timestamp to readable Tashkent (UTC+5) string."""
    if not iso_str:
        return "yo'q"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        tashkent_tz = timezone(timedelta(hours=5))
        dt_local = dt.astimezone(tashkent_tz)
        return dt_local.strftime("%d.%m.%Y, %H:%M")
    except Exception:
        return str(iso_str)[:16].replace("T", " ")



@router.message(Command("users", "admin_users", "secret_users"))
async def cmd_users_overview(message: Message, command: CommandObject) -> None:
    """Secret and secure command to view all users, balances, and listings.

    Only accessible by authorized administrators (via is_admin in DB, ADMIN_TG_IDS, or secret key).
    """
    token_arg = (command.args or "").strip()
    caller_tg_id = message.from_user.id if message.from_user else 0

    url = f"{BACKEND_URL}/api/v1/users/admin/overview"
    headers = {"X-Internal-Token": INTERNAL_API_TOKEN}
    params: dict[str, Any] = {"caller_tg_id": caller_tg_id}
    if token_arg:
        params["secret_key"] = token_arg

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers, params=params)

        if resp.status_code == 403:
            logger.warning("Unauthorized /users attempt by tg_id=%s", caller_tg_id)
            # Secret command: do not disclose command details to unauthorized users
            await message.answer("Noma'lum buyruq. /start ni bosing.")
            return

        if resp.status_code != 200:
            logger.error("Failed to fetch admin overview: status=%s body=%s", resp.status_code, resp.text)
            await message.answer("Ma'lumotlarni yuklashda xatolik yuz berdi.")
            return

        data = resp.json()
        users = data.get("users", [])
        total_users = data.get("total_users", len(users))
        total_listings = data.get("total_listings", 0)

        header_text = (
            "👑 <b>Rung — Foydalanuvchilar va Balanslar</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{total_users} ta</b>\n"
            f"📢 Jami faol kanallar: <b>{total_listings} ta</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        blocks: list[str] = []
        for i, u in enumerate(users, 1):
            fname = html.escape(u.get("first_name") or "Noma'lum")
            tg_id = u.get("telegram_id")
            if u.get("username"):
                uname = f"@{html.escape(u['username'])}"
            elif tg_id:
                uname = f'<a href="tg://user?id={tg_id}">havola orqali kirish ↗</a>'
            else:
                uname = "yo'q"

            bal_b = u.get("balance_b", 0)
            bal_som = u.get("balance_som", "0")
            dep_b = u.get("total_deposited_b", 0)
            spent_b = u.get("total_spent_b", 0)
            is_adm = " ⭐️ [ADMIN]" if u.get("is_admin") else ""
            listings = u.get("listings", [])

            created_str = format_tashkent_time(u.get("created_at"))
            last_action_str = format_tashkent_time(u.get("last_action_at"))

            block = (
                f"<b>{i}. {fname}</b> ({uname}){is_adm}\n"
                f"   🆔 TG ID: <code>{tg_id}</code>\n"
                f"   📅 Qo'shilgan: <b>{created_str}</b>\n"
                f"   💰 Balans: <b>{bal_b} B</b> ({bal_som} so'm)\n"
                f"   💳 To'ldirgan: <b>{dep_b} B</b> | 📉 Sarflagan: <b>{spent_b} B</b>\n"
            )
            if last_action_str != "yo'q":
                block += f"   ⚡️ Oxirgi amal: <b>{last_action_str}</b>\n"

            if listings:
                block += f"   📢 Kanallari ({len(listings)} ta):\n"
                for l in listings:
                    lhandle = html.escape(l.get('handle') or '')
                    lname = html.escape(l.get('name') or '')
                    rank = l.get('rank')
                    subs = l.get('subscribers', 0)
                    rank_str = f"#{rank}-o'rinda" if rank else "doskada emas"
                    subs_str = f", {subs:,} obunachi".replace(",", " ") if subs else ""
                    block += f"      • {lhandle} — <i>{lname}</i> ({rank_str}{subs_str})\n"
            else:
                block += "   📢 Kanallari: <i>yo'q</i>\n"

            blocks.append(block)

        # Send in messages respecting Telegram's 4096 character limit
        current_msg = header_text
        for b in blocks:
            if len(current_msg) + len(b) > 3800:
                await message.answer(current_msg, parse_mode="HTML")
                current_msg = ""
            current_msg += b + "\n"

        if current_msg.strip():
            await message.answer(current_msg, parse_mode="HTML")

    except Exception as exc:
        logger.exception("Error in /users command: %s", exc)
        await message.answer("Tizimda xatolik yuz berdi. Keyinroq urinib ko'ring.")
