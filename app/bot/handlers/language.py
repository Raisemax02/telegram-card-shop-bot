"""Language selection handler — User language preference."""

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.i18n import get_available_languages, get_locale, set_user_language
from app.bot.keyboards import make_button

from .helpers import fsm_timestamps, show_main_menu, update_message

logger = logging.getLogger(__name__)
router = Router(name="language")


@router.callback_query(F.data == "language")
async def show_language_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Show language selection menu."""
    await state.clear()
    fsm_timestamps.pop(callback.from_user.id, None)

    user_id = callback.from_user.id
    t = get_locale(user_id)
    available = get_available_languages()

    # Build keyboard with all available languages
    rows: list[list[InlineKeyboardButton]] = []
    for lang_code, lang_name in available.items():
        # Get flag and name from the locale module
        try:
            locale_module = __import__(f"app.bot.i18n.{lang_code}", fromlist=["FLAG", "LANG_NAME"])
            flag = getattr(locale_module, "FLAG", "🌍")
        except (ImportError, AttributeError):
            logger.warning("Failed to load locale module for '%s'", lang_code)
            flag = "🌍"
        button_text = f"{flag} {lang_name}"
        rows.append([make_button(button_text, f"setlang_{lang_code}")])

    rows.append([make_button(t.BTN_BACK, "home")])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await update_message(callback, t.MSG_SELECT_LANGUAGE, kb)


@router.callback_query(F.data.startswith("setlang_"))
async def set_language(callback: CallbackQuery) -> None:
    """Set user's language preference."""
    parts = callback.data.split("_")
    if len(parts) < 2:
        return

    lang_code = parts[1]
    user_id = callback.from_user.id

    if set_user_language(user_id, lang_code):
        t = get_locale(user_id)  # Get new locale
        await callback.answer(t.MSG_LANGUAGE_CHANGED, show_alert=True)
        await show_main_menu(callback)
    else:
        await callback.answer("Error setting language", show_alert=True)
