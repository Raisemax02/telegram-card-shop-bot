"""
Inline keyboards — InlineKeyboardMarkup generators.

All bot keyboards are created here.
Uses i18n for button labels.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .config import CATEGORY_NAMES
from .i18n import get_locale

# Button width constants for uniform sizing
BTN_WIDTH_WIDE = 20  # Full-width buttons
BTN_WIDTH_MEDIUM = 10  # Half-width buttons
BTN_WIDTH_NARROW = 6  # Third-width buttons


def make_button(text: str, callback_data: str, width: str = "wide") -> InlineKeyboardButton:
    """Create a button with uniform width by centering text.

    Args:
        text: Button text (emoji + label)
        callback_data: Callback data string
        width: Button width - "wide", "medium", or "narrow"
    """
    width_map = {
        "wide": BTN_WIDTH_WIDE,
        "medium": BTN_WIDTH_MEDIUM,
        "narrow": BTN_WIDTH_NARROW,
    }
    max_width = width_map.get(width, BTN_WIDTH_WIDE)

    # Calculate padding needed to center the text
    text_len = len(text)
    if text_len >= max_width:
        # Text is too long, truncate if necessary
        final_text = text[:max_width]
    else:
        # Center the text
        total_padding = max_width - text_len
        left_padding = total_padding // 2
        right_padding = total_padding - left_padding
        final_text = " " * left_padding + text + " " * right_padding

    return InlineKeyboardButton(text=final_text, callback_data=callback_data)


def get_main_menu(user_id: int | None = None) -> InlineKeyboardMarkup:
    """Main menu keyboard — 3 rows."""
    t = get_locale(user_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [make_button(t.BTN_MENU_CARDS, "menu")],
            [make_button(t.BTN_REVIEWS, "recensioni")],
            [
                make_button(t.BTN_INFO, "info", "medium"),
                make_button(t.BTN_CONTACTS, "contatti", "medium"),
            ],
            [
                make_button(t.BTN_LANGUAGE, "language", "medium"),
            ],
        ]
    )


def get_categories_menu(user_id: int | None = None) -> InlineKeyboardMarkup:
    """Category selection keyboard with back button."""
    t = get_locale(user_id)
    rows: list[list[InlineKeyboardButton]] = []
    for cat_id, cat_name in CATEGORY_NAMES.items():
        rows.append([make_button(cat_name, f"cat_{cat_id}")])
    rows.append([make_button(t.BTN_BACK, "home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_back_button(destination: str = "home", user_id: int | None = None) -> InlineKeyboardMarkup:
    """Keyboard with only a Back button."""
    t = get_locale(user_id)
    return InlineKeyboardMarkup(inline_keyboard=[[make_button(f"🔙 {t.BTN_BACK}", destination)]])


def get_cancel_button(destination: str = "home", user_id: int | None = None) -> InlineKeyboardMarkup:
    """Keyboard with only a Cancel button."""
    t = get_locale(user_id)
    return InlineKeyboardMarkup(inline_keyboard=[[make_button(f"❌ {t.BTN_CANCEL}", destination)]])
