"""Handler utilities — Shared state and helper functions."""

import asyncio
import functools
import logging
import time
from collections import defaultdict
from collections.abc import Callable

from aiogram import types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup

from app.bot.config import FSM_TIMEOUT_SECONDS, RATE_LIMIT_WINDOW, WELCOME_IMAGE_PATH
from app.bot.i18n import get_locale
from app.bot.keyboards import get_main_menu

logger = logging.getLogger(__name__)

# Rate-limit registry: {user_id: [timestamp, ...]}
rate_limit_registry: dict[int, list[float]] = defaultdict(list)
RATE_LIMIT_MAX_MESSAGES = 5  # Max messages allowed within the window

# Review rate limiting: {user_id: [timestamp, ...]} - max 3 reviews per hour
review_rate_limit_registry: dict[int, list[float]] = defaultdict(list)
REVIEW_RATE_LIMIT_MAX = 3  # Max reviews per hour
REVIEW_RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

# Last FSM action timestamp per admin
fsm_timestamps: dict[int, float] = {}

# Cached file_id for the welcome photo (avoids re-upload)
_welcome_photo_id: str | None = None

# Tracked deletion tasks — allows graceful shutdown
_pending_deletions: set[asyncio.Task] = set()


async def delete_message_after(message: types.Message, delay: int) -> None:
    """Delete a message after N seconds (video privacy).

    The active task is tracked in _pending_deletions so it can be
    cancelled cleanly on shutdown.
    """
    task = asyncio.current_task()
    if task is not None:
        _pending_deletions.add(task)
    try:
        await asyncio.sleep(delay)
        try:
            await message.delete()
            logger.info("Message %s auto-deleted after %ds", message.message_id, delay)
        except Exception:
            logger.debug("Could not delete message %s", message.message_id)
    finally:
        if task is not None:
            _pending_deletions.discard(task)


async def check_fsm_timeout(state: FSMContext, user_id: int) -> bool:
    """Verify FSM session hasn't expired. Returns True if still valid."""
    now = time.time()
    last_action = fsm_timestamps.get(user_id, 0)

    if last_action > 0 and (now - last_action) > FSM_TIMEOUT_SECONDS:
        await state.clear()
        fsm_timestamps.pop(user_id, None)
        logger.info("FSM session expired for admin %s", user_id)
        return False

    fsm_timestamps[user_id] = now
    return True


def check_rate_limit(user_id: int) -> bool:
    """Return True if the user can send, False if rate-limited.

    Allows up to RATE_LIMIT_MAX_MESSAGES messages within RATE_LIMIT_WINDOW seconds.
    """
    now = time.time()
    timestamps = rate_limit_registry[user_id]
    timestamps[:] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]

    if len(timestamps) >= RATE_LIMIT_MAX_MESSAGES:
        return False
    timestamps.append(now)
    return True


def check_review_rate_limit(user_id: int) -> tuple[bool, int]:
    """Check if user can leave another review.

    Returns:
        Tuple of (can_review: bool, remaining_time_seconds: int)
    """
    now = time.time()
    timestamps = review_rate_limit_registry[user_id]

    # Remove old timestamps outside the window
    timestamps[:] = [t for t in timestamps if now - t < REVIEW_RATE_LIMIT_WINDOW]

    # Check if limit reached
    if len(timestamps) >= REVIEW_RATE_LIMIT_MAX:
        # Calculate time until oldest review expires
        oldest = min(timestamps)
        remaining = int(REVIEW_RATE_LIMIT_WINDOW - (now - oldest))
        return False, remaining

    # Add current timestamp
    timestamps.append(now)
    return True, 0


async def send_menu_with_photo(
    target: types.Message,
    text: str,
    kb: InlineKeyboardMarkup,
) -> types.Message:
    """Send the welcome photo with caption and keyboard.

    Uses cached file_id when available to avoid re-upload.
    Falls back to text message if the photo file doesn't exist.
    """
    global _welcome_photo_id  # noqa: PLW0603

    # Use cached file_id if available (fast path)
    if _welcome_photo_id:
        try:
            return await target.answer_photo(
                photo=_welcome_photo_id,
                caption=text,
                reply_markup=kb,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            _welcome_photo_id = None  # Invalidate cache

    # First time: upload from disk
    if WELCOME_IMAGE_PATH.is_file():
        try:
            msg = await target.answer_photo(
                photo=FSInputFile(WELCOME_IMAGE_PATH),
                caption=text,
                reply_markup=kb,
                parse_mode=ParseMode.MARKDOWN,
            )
            if msg.photo:
                _welcome_photo_id = msg.photo[-1].file_id
            return msg
        except Exception:
            logger.exception("Failed to send welcome photo")

    # Fallback: no photo available -> text message
    return await target.answer(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)


async def show_main_menu(callback: CallbackQuery) -> None:
    """Show the main menu. Always deletes current message and resends with photo."""
    user_id = callback.from_user.id
    t = get_locale(user_id)
    kb = get_main_menu(user_id)

    try:
        await callback.message.delete()
    except Exception:
        logger.debug("Could not delete message, proceeding with resend")

    await send_menu_with_photo(callback.message, t.MSG_START, kb)


async def update_message(
    callback: CallbackQuery,
    text: str,
    kb: InlineKeyboardMarkup,
) -> None:
    """Update the current message in-place. No resend, only edit."""
    # If it's a photo or video message, we need to delete and resend as text
    if callback.message.photo or callback.message.video:
        try:
            await callback.message.delete()
            await callback.message.answer(text, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            logger.debug("Failed to switch from photo/video to text message")
        return

    # Regular text message: edit in place
    try:
        await callback.message.edit_text(
            text,
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception:
        logger.debug("Could not edit message text")


# =============================================================================
# SAFE CALLBACK DECORATOR
# =============================================================================
def safe_callback(func: Callable) -> Callable:
    """Decorator that wraps callback handlers with top-level exception handling.

    Prevents the bot from becoming unresponsive when an unhandled
    exception occurs in a callback handler.
    """

    @functools.wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        try:
            return await func(callback, *args, **kwargs)
        except Exception:
            logger.exception("Unhandled error in handler %s", func.__name__)
            try:
                await callback.answer("⚠️ An error occurred. Please try again.", show_alert=True)
            except Exception:
                logger.debug("Could not send error answer to user")

    return wrapper


def cancel_pending_deletions() -> None:
    """Cancel all pending message-deletion tasks (called on shutdown)."""
    for task in _pending_deletions.copy():
        task.cancel()
    logger.info("Cancelled %d pending deletion task(s)", len(_pending_deletions))
    _pending_deletions.clear()
