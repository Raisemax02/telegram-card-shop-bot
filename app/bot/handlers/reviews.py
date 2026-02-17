"""
Review handlers — Review workflow for cards.

Handles: review_*, rate_*, comment_skip,
         and FSM states for leaving reviews.
"""

import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from app.bot.audit import log_security_event
from app.bot.database import add_review, get_card, user_has_reviewed
from app.bot.i18n import get_locale
from app.bot.keyboards import make_button

from .helpers import check_review_rate_limit, update_message
from .states import LeaveReview

logger = logging.getLogger(__name__)
router = Router(name="reviews")


@router.callback_query(F.data.startswith("review_"))
async def start_review(callback: CallbackQuery, state: FSMContext) -> None:
    """Start the review workflow for a card."""
    parts = callback.data.split("_")
    if len(parts) < 2:
        return

    card_id = parts[1]
    user_id = callback.from_user.id
    t = get_locale(user_id)

    # Check review rate limit (max 3 reviews per hour)
    can_review, remaining_seconds = check_review_rate_limit(user_id)
    if not can_review:
        minutes = (remaining_seconds // 60) + 1
        log_security_event("RATE_LIMIT", user_id, f"review_attempt | remaining={remaining_seconds}s")
        await callback.answer(t.WARN_REVIEW_RATE_LIMIT.format(minutes=minutes), show_alert=True)
        return

    card = await get_card(card_id)
    if not card:
        await callback.answer(t.WARN_CARD_NOT_FOUND, show_alert=True)
        return

    # Check if user has already reviewed this card
    if await user_has_reviewed(int(card_id), user_id):
        log_security_event("DUPLICATE_REVIEW", user_id, f"card_id={card_id}")
        await callback.answer(t.WARN_ALREADY_REVIEWED, show_alert=True)
        return

    title = card.get("title", "N/A")
    await state.update_data(card_id=card_id, card_title=title)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                make_button("⭐ 1", "rate_1", "narrow"),
                make_button("⭐ 2", "rate_2", "narrow"),
                make_button("⭐ 3", "rate_3", "narrow"),
            ],
            [
                make_button("⭐ 4", "rate_4", "narrow"),
                make_button("⭐ 5", "rate_5", "narrow"),
            ],
            [make_button(f"❌ {t.BTN_CANCEL}", f"view_{card_id}")],
        ]
    )

    await update_message(callback, t.MSG_START_REVIEW.format(title=title), kb)
    await state.set_state(LeaveReview.choose_rating)


@router.callback_query(F.data.startswith("rate_"))
async def select_rating(callback: CallbackQuery, state: FSMContext) -> None:
    """Receive the rating (1-5)."""
    parts = callback.data.split("_")
    if len(parts) < 2:
        return

    rating = int(parts[1])
    await state.update_data(rating=rating)

    data = await state.get_data()
    title = data.get("card_title", "Carta")
    user_id = callback.from_user.id
    t = get_locale(user_id)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [make_button(f"⏩ {t.BTN_SKIP_COMMENT}", "comment_skip")],
            [make_button(f"❌ {t.BTN_CANCEL}", f"view_{data['card_id']}")],
        ]
    )

    await update_message(callback, t.MSG_WRITE_COMMENT.format(rating=rating, title=title), kb)
    await state.set_state(LeaveReview.write_comment)


@router.message(LeaveReview.write_comment)
async def save_review_with_comment(message: types.Message, state: FSMContext) -> None:
    """Save the review with a comment."""
    user_id = message.from_user.id
    t = get_locale(user_id)

    if not message.text:
        await message.answer(t.WARN_WRITE_COMMENT)
        return

    if len(message.text) > 200:
        await message.answer(t.WARN_COMMENT_TOO_LONG)
        return

    data = await state.get_data()

    try:
        await add_review(
            card_id=int(data["card_id"]),
            user_id=user_id,
            rating=data["rating"],
            comment=message.text,
        )
        await message.answer(t.CONFIRM_REVIEW)
    except ValueError:
        # User already reviewed (shouldn't happen due to pre-check, but just in case)
        logger.warning("User %s tried to review card %s twice", user_id, data["card_id"])
        await message.answer(t.WARN_ALREADY_REVIEWED)
    except Exception:
        logger.exception("Failed to save review")
        await message.answer(t.ERR_SAVE_REVIEW)

    await state.clear()


@router.callback_query(F.data == "comment_skip")
async def skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    """Save review without a comment."""
    data = await state.get_data()
    user_id = callback.from_user.id
    t = get_locale(user_id)

    try:
        await add_review(
            card_id=int(data["card_id"]),
            user_id=user_id,
            rating=data["rating"],
            comment="",
        )
        await callback.answer(t.MSG_REVIEW_SAVED)
    except ValueError:
        logger.warning("User %s tried to review card %s twice", user_id, data["card_id"])
        await callback.answer(t.WARN_ALREADY_REVIEWED, show_alert=True)
    except Exception:
        logger.exception("Failed to save review")
        await callback.answer(t.ERR_SAVE_REVIEW, show_alert=True)

    await state.clear()

    # Redirect back to card view
    from .cards import view_card

    callback.data = f"view_{data['card_id']}"
    await view_card(callback)
