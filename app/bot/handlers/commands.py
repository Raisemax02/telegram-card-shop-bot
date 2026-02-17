"""Command handlers — /start and /admin commands."""

import logging

from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart

from app.bot.config import ADMIN_IDS
from app.bot.i18n import get_locale
from app.bot.keyboards import get_main_menu

from .helpers import send_menu_with_photo

logger = logging.getLogger(__name__)
router = Router(name="commands")


@router.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    """Handle /start — Welcome photo + main menu."""
    user_id = message.from_user.id
    t = get_locale(user_id)
    logger.info("User %s started the bot", user_id)
    await send_menu_with_photo(message, t.MSG_START, get_main_menu(user_id))


@router.message(Command("admin"))
async def cmd_admin(message: types.Message) -> None:
    """Handle /admin — Admin-only access."""
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        logger.warning("Unauthorized admin access attempt from user %s", user_id)
        return

    t = get_locale(user_id)
    await message.answer(
        t.MSG_ADMIN_PANEL,
        reply_markup=get_main_menu(user_id),
        parse_mode=ParseMode.MARKDOWN,
    )
