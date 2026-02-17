"""
Anti-spam handler — Blocks unsolicited messages from non-admin users.

This handler MUST be registered last, as it catches all message types.
"""

import asyncio
import logging

from aiogram import F, Router, types
from aiogram.enums import ParseMode

from app.bot.config import ADMIN_IDS, WARNING_MESSAGE_DURATION
from app.bot.i18n import get_locale

from .helpers import check_rate_limit

logger = logging.getLogger(__name__)
router = Router(name="antispam")


@router.message(F.text | F.photo | F.video | F.document | F.sticker | F.voice | F.audio)
async def block_unsolicited_messages(message: types.Message) -> None:
    """Block unsolicited messages from non-admin users."""
    if message.from_user.id in ADMIN_IDS:
        return

    if not check_rate_limit(message.from_user.id):
        try:
            await message.delete()
        except Exception:
            logger.debug("Could not delete rate-limited message from user %s", message.from_user.id)
        return

    user_id = message.from_user.id
    t = get_locale(user_id)

    logger.info("Blocked message from user %s", user_id)
    try:
        await message.delete()
        warning = await message.answer(t.WARN_SPAM, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(WARNING_MESSAGE_DURATION)
        await warning.delete()
    except Exception:
        logger.debug("Error blocking spam from user %s", user_id)
