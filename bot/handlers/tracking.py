import os
import logging
from aiogram import Router, F
from aiogram.types import ChatMemberUpdated, Message
import httpx

logger = logging.getLogger(__name__)

router = Router()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")

async def send_event_to_backend(payload: dict) -> dict | None:
    if not INTERNAL_API_TOKEN:
        logger.warning("No INTERNAL_API_TOKEN set, skipping subscriber event")
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{BACKEND_URL}/api/v1/internal/bot/events/subscriber",
                json=payload,
                headers={"X-Internal-Token": INTERNAL_API_TOKEN}
            )
            if not res.is_success:
                logger.error(f"Failed to send subscriber event to backend: {res.status_code} {res.text}")
                return None
            return res.json()
    except Exception as e:
        logger.error(f"Exception sending subscriber event to backend: {e}")
        return None

import json
from aiogram import Bot

SUBSCRIBER_NOTIFY_USER_IDS_STR = os.getenv("SUBSCRIBER_NOTIFY_USER_IDS", "[557407324]")
try:
    SUBSCRIBER_NOTIFY_USER_IDS = set(json.loads(SUBSCRIBER_NOTIFY_USER_IDS_STR))
except Exception:
    SUBSCRIBER_NOTIFY_USER_IDS = {557407324}

def get_user_info(user) -> str:
    if getattr(user, 'username', None):
        return f"@{user.username}"
    elif getattr(user, 'first_name', None):
        return user.first_name
    return "obunachi"

async def notify_owner(bot: Bot, response: dict | None, action: str, user_info: str, chat_title: str):
    # TODO: This is a temporary test-phase simplification.
    # Once validated, switch back to routing to the real listing owner:
    # owner_id = response.get("owner_telegram_id")
    # if owner_id and owner_id in SUBSCRIBER_NOTIFY_USER_IDS: ...

    listing_name = chat_title
    if response and response.get("status") == "ok":
        listing_name = response.get("listing_name", chat_title)
        
    action_text = "obunachi qo'shildi" if action == "join" else "obunachi chiqib ketdi"
    icon = "📥" if action == "join" else "📤"
    msg = f"{icon} {listing_name}: {action_text}\n(Kim: {user_info})"
    
    for admin_id in SUBSCRIBER_NOTIFY_USER_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=msg, disable_notification=True)
            logger.info(f"Sent silent subscriber notification to test admin {admin_id}")
        except Exception as e:
            logger.warning(f"Failed to send notification to test admin {admin_id}: {e}")

@router.my_chat_member()
async def on_my_chat_member(update: ChatMemberUpdated):
    """Fired when the bot's own member status changes (e.g. promoted to admin or kicked)."""
    is_bot_admin = update.new_chat_member.status in ("administrator", "creator")
    
    payload = {
        "telegram_chat_id": update.chat.id,
        "chat_username": update.chat.username,
        "action": "status_change",
        "source": update.chat.type,
        "is_bot_admin": is_bot_admin
    }
    await send_event_to_backend(payload)

@router.chat_member()
async def on_chat_member(update: ChatMemberUpdated, bot: Bot):
    """Fired when a user joins or leaves a channel (or group if configured, though group uses message for backwards compatibility)."""
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status

    # Ignore bot's own updates here, handled by my_chat_member
    if update.new_chat_member.user.is_bot:
        return

    action = None
    if old_status in ("left", "kicked") and new_status in ("member", "administrator", "creator"):
        action = "join"
    elif old_status in ("member", "administrator", "creator") and new_status in ("left", "kicked"):
        action = "leave"

    if action:
        payload = {
            "telegram_chat_id": update.chat.id,
            "telegram_user_id": update.new_chat_member.user.id,
            "chat_username": update.chat.username,
            "action": action,
            "source": update.chat.type,
        }
        res = await send_event_to_backend(payload)
        user_info = get_user_info(update.new_chat_member.user)
        chat_title = getattr(update.chat, 'title', None) or getattr(update.chat, 'username', None) or "Kanal/Guruh"
        await notify_owner(bot, res, action, user_info, chat_title)

@router.message(F.new_chat_members)
async def on_user_join_group(message: Message, bot: Bot):
    """Fired when user(s) join a group."""
    if not message.new_chat_members:
        return
        
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        payload = {
            "telegram_chat_id": message.chat.id,
            "telegram_user_id": user.id,
            "chat_username": message.chat.username,
            "action": "join",
            "source": message.chat.type,
        }
        res = await send_event_to_backend(payload)
        user_info = get_user_info(user)
        chat_title = getattr(message.chat, 'title', None) or getattr(message.chat, 'username', None) or "Kanal/Guruh"
        await notify_owner(bot, res, "join", user_info, chat_title)

@router.message(F.left_chat_member)
async def on_user_leave_group(message: Message, bot: Bot):
    """Fired when a user leaves a group."""
    if not message.left_chat_member or message.left_chat_member.is_bot:
        return

    payload = {
        "telegram_chat_id": message.chat.id,
        "telegram_user_id": message.left_chat_member.id,
        "chat_username": message.chat.username,
        "action": "leave",
        "source": message.chat.type,
    }
    res = await send_event_to_backend(payload)
    user_info = get_user_info(message.left_chat_member)
    chat_title = getattr(message.chat, 'title', None) or getattr(message.chat, 'username', None) or "Kanal/Guruh"
    await notify_owner(bot, res, "leave", user_info, chat_title)
