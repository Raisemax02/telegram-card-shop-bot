"""Navigation handlers — Menu navigation callbacks.

Handles: home, info, contatti, recensioni, menu.
"""

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.bot.database import calculate_review_average, get_all_cards
from app.bot.i18n import get_locale
from app.bot.keyboards import get_back_button, get_categories_menu

from .helpers import fsm_timestamps, show_main_menu, update_message

logger = logging.getLogger(__name__)
router = Router(name="navigation")


@router.callback_query(F.data.in_({"info", "contatti", "recensioni", "menu", "home"}))
async def menu_navigation(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle navigation between menu sections."""
    await state.clear()
    fsm_timestamps.pop(callback.from_user.id, None)

    user_id = callback.from_user.id
    t = get_locale(user_id)

    if callback.data == "home":
        await show_main_menu(callback)
        return

    if callback.data == "info":
        await update_message(callback, t.MSG_INFO, get_back_button("home", user_id))
        return

    if callback.data == "contatti":
        await update_message(callback, t.MSG_CONTACTS, get_back_button("home", user_id))
        return

    if callback.data == "menu":
        await update_message(callback, t.MSG_CATEGORIES_MENU, get_categories_menu(user_id))
        return

    if callback.data == "recensioni":
        await _show_reviews(callback)


async def _show_reviews(callback: CallbackQuery) -> None:
    """Build and display the reviews summary."""
    user_id = callback.from_user.id
    t = get_locale(user_id)

    try:
        all_cards = await get_all_cards()

        if not all_cards:
            msg = t.MSG_REVIEWS_TITLE + t.NO_REVIEWS
        else:
            msg = t.MSG_REVIEWS_TITLE
            total_reviews = 0
            total_rating = 0

            for card in all_cards:
                reviews = card.get("reviews", [])
                if reviews:
                    average = calculate_review_average(reviews)
                    msg += t.ROW_CARD_REVIEW.format(
                        title=card["title"],
                        average=average,
                        count=len(reviews),
                    )
                    total_reviews += len(reviews)
                    total_rating += sum(r.get("rating", 0) for r in reviews)

            if total_reviews > 0:
                overall_average = total_rating / total_reviews
                msg += t.ROW_OVERALL_RATING.format(
                    average=overall_average,
                    total=total_reviews,
                )
            else:
                msg += t.NO_REVIEWS

    except Exception:
        logger.exception("Failed to load reviews")
        msg = t.ERR_REVIEWS_LOAD

    await update_message(callback, msg, get_back_button("home", user_id))
