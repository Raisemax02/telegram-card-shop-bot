"""
Card handlers — Category browsing, card viewing, and admin operations.

Handles: cat_*, view_*, addnew_*, delete_*, confdelete_*, updatevideo_*,
         and FSM states for card upload and video update.
"""

import asyncio
import logging
import time

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.config import (
    ADMIN_IDS,
    AUTO_DELETE_VIDEO_SECONDS,
    CARDS_PER_PAGE,
    CATEGORY_NAMES,
    MAX_BUTTON_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_TITLE_LENGTH,
    MAX_VIDEO_SIZE_MB,
)
from app.bot.database import (
    add_card,
    calculate_review_average,
    delete_card,
    get_card,
    get_cards,
    update_card_description,
    update_card_title,
    update_card_video,
    validate_category,
    validate_video_mimetype,
)
from app.bot.i18n import get_locale
from app.bot.keyboards import get_cancel_button, get_main_menu, make_button

from .helpers import check_fsm_timeout, delete_message_after, fsm_timestamps, send_menu_with_photo, update_message
from .states import UpdateCardDescription, UpdateCardTitle, UpdateCardVideo, UploadCard

logger = logging.getLogger(__name__)
router = Router(name="cards")


# =============================================================================
# FSM: CARD UPLOAD (Admin only)
# =============================================================================
@router.message(UploadCard.write_title)
async def admin_receive_title(message: types.Message, state: FSMContext) -> None:
    """FSM: receive the card title."""
    user_id = message.from_user.id
    t = get_locale(user_id)

    if not await check_fsm_timeout(state, user_id):
        await message.answer(
            t.WARN_SESSION_EXPIRED,
            reply_markup=get_main_menu(user_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if not message.text:
        await message.answer(t.WARN_TEXT_REQUIRED)
        return

    if len(message.text) > MAX_TITLE_LENGTH:
        await message.answer(t.WARN_TITLE_TOO_LONG.format(max=MAX_TITLE_LENGTH))
        return

    await state.update_data(title=message.text)
    logger.info("Admin %s set title: %s", user_id, message.text[:50])

    await message.answer(
        t.MSG_TITLE_OK.format(title=message.text),
        reply_markup=get_cancel_button("home", user_id),
        parse_mode=ParseMode.MARKDOWN,
    )
    await state.set_state(UploadCard.send_video)


@router.message(UploadCard.send_video, F.video)
async def admin_receive_video(message: types.Message, state: FSMContext) -> None:
    """FSM: receive the card video."""
    user_id = message.from_user.id
    t = get_locale(user_id)

    if not await check_fsm_timeout(state, user_id):
        await message.answer(
            t.WARN_SESSION_EXPIRED,
            reply_markup=get_main_menu(user_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if message.video.file_size and message.video.file_size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        await message.answer(t.WARN_VIDEO_TOO_LARGE.format(max=MAX_VIDEO_SIZE_MB))
        return

    # Validate video format (mime type check)
    if not validate_video_mimetype(message.video.file_name):
        await message.answer(t.WARN_INVALID_VIDEO_FORMAT)
        return

    await state.update_data(video_id=message.video.file_id)
    logger.info("Admin %s sent video: ...%s", user_id, message.video.file_id[-10:])

    await message.answer(
        t.MSG_VIDEO_OK.format(max_len=MAX_DESCRIPTION_LENGTH),
        reply_markup=get_cancel_button("home", user_id),
        parse_mode=ParseMode.MARKDOWN,
    )
    await state.set_state(UploadCard.write_description)


@router.message(UploadCard.send_video)
async def admin_video_error(message: types.Message) -> None:
    """FSM: admin sent something that is not a video."""
    t = get_locale(message.from_user.id)
    await message.answer(t.WARN_VIDEO_REQUIRED, parse_mode=ParseMode.MARKDOWN)


@router.message(UploadCard.write_description)
async def admin_save_card(message: types.Message, state: FSMContext) -> None:
    """FSM: receive description, validate, and save the card."""
    user_id = message.from_user.id
    t = get_locale(user_id)

    if not await check_fsm_timeout(state, user_id):
        await message.answer(
            t.WARN_SESSION_EXPIRED,
            reply_markup=get_main_menu(user_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if not message.text:
        await message.answer(t.WARN_DESCRIPTION_REQUIRED)
        return

    if len(message.text) > MAX_DESCRIPTION_LENGTH:
        await message.answer(t.WARN_DESCRIPTION_TOO_LONG.format(max=MAX_DESCRIPTION_LENGTH))
        return

    data = await state.get_data()

    if not all(k in data for k in ("category", "title", "video_id")):
        await message.answer(t.WARN_MISSING_DATA)
        await state.clear()
        fsm_timestamps.pop(user_id, None)
        return

    if not validate_category(data["category"]):
        await message.answer(t.WARN_INVALID_CATEGORY)
        await state.clear()
        fsm_timestamps.pop(user_id, None)
        return

    try:
        await add_card(data["category"], data["title"], data["video_id"], message.text, admin_id=user_id)
        logger.info("Admin %s published card: %s", user_id, data["title"])

        cat_name = CATEGORY_NAMES.get(data["category"], data["category"])
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [make_button(f"📂 {t.BTN_BACK_TO_CAT.format(cat_name=cat_name)}", f"cat_{data['category']}")]
            ]
        )
        await message.answer(
            t.MSG_CARD_PUBLISHED,
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception:
        logger.exception("Failed to save card")
        await message.answer(t.WARN_SAVE_ERROR)
    finally:
        await state.clear()
        fsm_timestamps.pop(user_id, None)


# =============================================================================
# CATEGORY VIEW (with pagination)
# =============================================================================
@router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery) -> None:
    """Show cards in a category with pagination. Admins see Add + Delete buttons."""
    parts = callback.data.split("_")
    if len(parts) < 2:
        return

    category = parts[1]

    # Extract page number if present (format: cat_category_pN)
    page = 1
    if len(parts) >= 4 and parts[2] == "p":
        try:
            page = int(parts[3])
        except ValueError:
            page = 1

    user_id = callback.from_user.id
    t = get_locale(user_id)

    if not validate_category(category):
        await callback.answer(t.WARN_INVALID_CATEGORY, show_alert=True)
        return

    is_admin = user_id in ADMIN_IDS
    all_cards = await get_cards(category)
    cat_name = CATEGORY_NAMES.get(category, category.upper())

    # Calculate pagination
    total_cards = len(all_cards)
    total_pages = (total_cards + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE  # Ceiling division
    page = max(1, min(page, total_pages))  # Clamp page number

    start_idx = (page - 1) * CARDS_PER_PAGE
    end_idx = start_idx + CARDS_PER_PAGE
    cards_page = all_cards[start_idx:end_idx]

    logger.info("User %s -> %s (page %d/%d, %d total cards)", user_id, category, page, total_pages, total_cards)

    kb_rows: list[list[InlineKeyboardButton]] = []

    if is_admin:
        kb_rows.append([make_button(f"➕ {t.BTN_ADD_CARD}", f"addnew_{category}")])

    if cards_page:
        for card_id, card_title in cards_page:
            short_title = card_title[:MAX_BUTTON_LENGTH]
            if len(card_title) > MAX_BUTTON_LENGTH:
                short_title += "…"

            btn_view = make_button(f"🔹 {short_title}", f"view_{card_id}")

            if is_admin:
                btn_delete = InlineKeyboardButton(
                    text="🗑",
                    callback_data=f"delete_{card_id}_{category}",
                )
                kb_rows.append([btn_view, btn_delete])
            else:
                kb_rows.append([btn_view])

    # Pagination buttons
    if total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(make_button(t.BTN_PREVIOUS, f"cat_{category}_p_{page - 1}", "medium"))
        if page < total_pages:
            nav_buttons.append(make_button(t.BTN_NEXT, f"cat_{category}_p_{page + 1}", "medium"))
        if nav_buttons:
            kb_rows.append(nav_buttons)

    kb_rows.append([make_button(f"🔙 {t.BTN_CATEGORIES_MENU}", "menu")])

    # Text with page info
    text = t.MSG_CATEGORY.format(cat_name=cat_name)
    if total_pages > 1:
        text += f"\n\n📄 {t.LBL_PAGE} {page}/{total_pages}"
    if not all_cards:
        text += t.NO_CARDS

    await update_message(callback, text, InlineKeyboardMarkup(inline_keyboard=kb_rows))


# =============================================================================
# ADD CARD (Admin only)
# =============================================================================
@router.callback_query(F.data.startswith("addnew_"))
async def start_add_card(callback: CallbackQuery, state: FSMContext) -> None:
    """Start the card upload workflow."""
    user_id = callback.from_user.id
    t = get_locale(user_id)

    if user_id not in ADMIN_IDS:
        await callback.answer(t.WARN_ACCESS_DENIED, show_alert=True)
        return

    parts = callback.data.split("_")
    if len(parts) < 2:
        return

    category = parts[1]
    if not validate_category(category):
        await callback.answer(t.WARN_INVALID_CATEGORY, show_alert=True)
        return

    await state.update_data(category=category)
    fsm_timestamps[user_id] = time.time()

    cat_name = CATEGORY_NAMES.get(category, category.upper())
    logger.info("Admin %s -> adding card in %s", user_id, category)

    await update_message(
        callback,
        t.MSG_WRITE_TITLE.format(cat_name=cat_name, max_len=MAX_TITLE_LENGTH),
        get_cancel_button(f"cat_{category}", user_id),
    )
    await state.set_state(UploadCard.write_title)


# =============================================================================
# DELETE CARD (Admin only) — Double confirmation
# =============================================================================
@router.callback_query(F.data.startswith("delete_"))
async def request_delete_card(callback: CallbackQuery) -> None:
    """Show confirmation before deletion."""
    parts = callback.data.split("_")
    if len(parts) < 3:
        return

    card_id = parts[1]
    category = parts[2]
    user_id = callback.from_user.id
    t = get_locale(user_id)

    if user_id not in ADMIN_IDS:
        await callback.answer(t.WARN_ACCESS_DENIED, show_alert=True)
        return

    card = await get_card(card_id)
    if not card:
        await callback.answer(t.WARN_CARD_NOT_FOUND, show_alert=True)
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [make_button(f"✅ {t.BTN_YES_DELETE}", f"confdelete_{card_id}_{category}")],
            [make_button(f"❌ {t.BTN_CANCEL}", f"cat_{category}")],
        ]
    )

    await update_message(
        callback,
        t.MSG_CONFIRM_DELETE.format(title=card.get("title", "N/A")),
        kb,
    )


@router.callback_query(F.data.startswith("confdelete_"))
async def confirm_delete_card(callback: CallbackQuery) -> None:
    """Execute the actual card deletion."""
    parts = callback.data.split("_")
    if len(parts) < 3:
        return

    card_id = parts[1]
    category = parts[2]
    user_id = callback.from_user.id
    t = get_locale(user_id)

    if user_id not in ADMIN_IDS:
        await callback.answer(t.WARN_ACCESS_DENIED, show_alert=True)
        return

    try:
        await delete_card(card_id, admin_id=user_id)
        logger.info("Admin %s deleted card %s", user_id, card_id)
        await callback.answer(t.MSG_CARD_DELETED)
    except Exception:
        logger.exception("Failed to delete card %s", card_id)
        await callback.answer(t.WARN_DELETE_ERROR, show_alert=True)
        return

    # Redirect back to category view
    callback.data = f"cat_{category}"
    await show_category(callback)


# =============================================================================
# CARD VIEW (Video)
# =============================================================================
@router.callback_query(F.data.startswith("view_"))
async def view_card(callback: CallbackQuery) -> None:
    """Show the card video. Auto-deletes for privacy."""
    parts = callback.data.split("_")
    if len(parts) < 2:
        return

    card_id = parts[1]
    user_id = callback.from_user.id
    t = get_locale(user_id)

    logger.info("User %s viewing card %s", user_id, card_id)

    card = await get_card(card_id)
    if not card:
        await callback.answer(t.WARN_CARD_NOT_FOUND, show_alert=True)
        try:
            await callback.message.delete()
        except Exception:
            logger.debug("Could not delete message after card not found")
        await send_menu_with_photo(callback.message, t.MSG_START, get_main_menu(user_id))
        return

    title = card.get("title", "N/A")
    video_id = card.get("video_id")
    description = card.get("description", "")
    category = card.get("category", "altro")
    reviews = card.get("reviews", [])
    average = calculate_review_average(reviews)

    # Admin: back button + update buttons. Users: also review button
    if user_id in ADMIN_IDS:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    make_button(t.BTN_EDIT_TITLE, f"updatetitle_{card_id}"),
                    make_button(t.BTN_EDIT_DESCRIPTION, f"updatedesc_{card_id}"),
                ],
                [make_button(t.BTN_UPDATE_VIDEO, f"updatevideo_{card_id}")],
                [make_button(f"🔙 {t.BTN_BACK}", f"cat_{category}")],
            ]
        )
    else:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [make_button(f"⭐ {t.BTN_LEAVE_REVIEW}", f"review_{card_id}")],
                [make_button(f"🔙 {t.BTN_BACK}", f"cat_{category}")],
            ]
        )

    caption = f"🏷 **{title}**\n\n{description}"
    if average > 0:
        caption += f"\n\n⭐ **{t.LBL_RATING}:** {average:.1f} ({len(reviews)} {t.LBL_REVIEWS})"

    # Delete previous message
    try:
        await callback.message.delete()
    except Exception:
        logger.debug("Could not delete previous message before video send")

    # Send the video
    try:
        video_msg = await callback.message.answer_video(
            video=video_id,
            caption=caption,
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )
        asyncio.create_task(delete_message_after(video_msg, AUTO_DELETE_VIDEO_SECONDS))
    except Exception as e:
        # Log warning without full traceback for invalid file IDs (common in test data)
        if "wrong remote file identifier" in str(e).lower() or "padding" in str(e).lower():
            logger.warning("Invalid or placeholder video_id for card %s: %s", card_id, video_id)
        else:
            logger.exception("Failed to send video %s", video_id)

        await callback.message.answer(
            f"{t.WARN_VIDEO_UNAVAILABLE}\n\n🏷 **{title}**\n\n{description}",
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )


# =============================================================================
# UPDATE CARD VIDEO (Admin only)
# =============================================================================
@router.callback_query(F.data.startswith("updatevideo_"))
async def start_update_video(callback: CallbackQuery, state: FSMContext) -> None:
    """Start the video update workflow."""
    user_id = callback.from_user.id
    t = get_locale(user_id)

    if user_id not in ADMIN_IDS:
        await callback.answer(t.WARN_ACCESS_DENIED, show_alert=True)
        return

    parts = callback.data.split("_")
    if len(parts) < 2:
        return

    card_id = parts[1]

    # Verify card exists
    card = await get_card(card_id)
    if not card:
        await callback.answer(t.WARN_CARD_NOT_FOUND, show_alert=True)
        return

    # Store card info in FSM
    await state.update_data(card_id=card_id, category=card.get("category", "altro"))
    await state.set_state(UpdateCardVideo.send_video)

    # Ask for new video
    kb = get_cancel_button(f"view_{card_id}", user_id)
    await update_message(
        callback,
        t.MSG_UPDATE_VIDEO.format(title=card.get("title", "N/A")),
        kb,
    )

    fsm_timestamps[user_id] = time.time()
    logger.info("Admin %s started video update for card %s", user_id, card_id)


@router.message(UpdateCardVideo.send_video, F.video)
async def receive_updated_video(message: types.Message, state: FSMContext) -> None:
    """Receive and save the new video."""
    user_id = message.from_user.id
    t = get_locale(user_id)

    if not await check_fsm_timeout(state, user_id):
        await message.answer(
            t.WARN_SESSION_EXPIRED,
            reply_markup=get_main_menu(user_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if message.video.file_size and message.video.file_size > MAX_VIDEO_SIZE_MB * 1024 * 1024:
        await message.answer(t.WARN_VIDEO_TOO_LARGE.format(max=MAX_VIDEO_SIZE_MB))
        return

    # Validate video format (mime type check)
    if not validate_video_mimetype(message.video.file_name):
        await message.answer(t.WARN_INVALID_VIDEO_FORMAT)
        return

    data = await state.get_data()
    card_id = data.get("card_id")
    category = data.get("category", "altro")

    if not card_id:
        await message.answer(t.WARN_MISSING_DATA)
        await state.clear()
        fsm_timestamps.pop(user_id, None)
        return

    try:
        # Update the video in the database
        await update_card_video(int(card_id), message.video.file_id, admin_id=user_id)
        logger.info("Admin %s updated video for card %s", user_id, card_id)

        # Clear FSM state
        await state.clear()
        fsm_timestamps.pop(user_id, None)

        # Send confirmation
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [make_button(t.BTN_BACK_TO_CATEGORY, f"cat_{category}")],
                [make_button(t.BTN_VIEW_CARD, f"view_{card_id}")],
            ]
        )
        await message.answer(
            t.MSG_VIDEO_UPDATED,
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception:
        logger.exception("Failed to update video for card %s", card_id)
        await message.answer(
            t.WARN_VIDEO_UPDATE_ERROR,
            reply_markup=get_main_menu(user_id),
            parse_mode=ParseMode.MARKDOWN,
        )


# =============================================================================
# UPDATE CARD TITLE (Admin only)
# =============================================================================
@router.callback_query(F.data.startswith("updatetitle_"))
async def start_update_title(callback: CallbackQuery, state: FSMContext) -> None:
    """Start the title update workflow."""
    user_id = callback.from_user.id
    t = get_locale(user_id)

    if user_id not in ADMIN_IDS:
        await callback.answer(t.WARN_ACCESS_DENIED, show_alert=True)
        return

    parts = callback.data.split("_")
    if len(parts) < 2:
        return

    card_id = parts[1]

    # Verify card exists
    card = await get_card(card_id)
    if not card:
        await callback.answer(t.WARN_CARD_NOT_FOUND, show_alert=True)
        return

    # Store card info in FSM
    await state.update_data(card_id=card_id, category=card.get("category", "altro"))
    await state.set_state(UpdateCardTitle.write_title)

    # Ask for new title
    kb = get_cancel_button(f"view_{card_id}", user_id)
    await update_message(
        callback,
        t.MSG_UPDATE_TITLE.format(title=card.get("title", "N/A"), max_len=MAX_TITLE_LENGTH),
        kb,
    )

    fsm_timestamps[user_id] = time.time()
    logger.info("Admin %s started title update for card %s", user_id, card_id)


@router.message(UpdateCardTitle.write_title, F.text)
async def receive_updated_title(message: types.Message, state: FSMContext) -> None:
    """Receive and save the new title."""
    user_id = message.from_user.id
    t = get_locale(user_id)

    if not await check_fsm_timeout(state, user_id):
        await message.answer(
            t.WARN_SESSION_EXPIRED,
            reply_markup=get_main_menu(user_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    new_title = message.text.strip()

    # Validate title length
    if len(new_title) > MAX_TITLE_LENGTH:
        await message.answer(t.WARN_TITLE_UPDATE_TOO_LONG.format(max_len=MAX_TITLE_LENGTH, current_len=len(new_title)))
        return

    if len(new_title) == 0:
        await message.answer(t.WARN_TITLE_EMPTY)
        return

    data = await state.get_data()
    card_id = data.get("card_id")
    category = data.get("category", "altro")

    if not card_id:
        await message.answer(t.WARN_MISSING_DATA)
        await state.clear()
        fsm_timestamps.pop(user_id, None)
        return

    try:
        # Update the title in the database
        await update_card_title(int(card_id), new_title, admin_id=user_id)
        logger.info("Admin %s updated title for card %s to '%s'", user_id, card_id, new_title)

        # Clear FSM state
        await state.clear()
        fsm_timestamps.pop(user_id, None)

        # Send confirmation
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [make_button(t.BTN_BACK_TO_CATEGORY, f"cat_{category}")],
                [make_button(t.BTN_VIEW_CARD, f"view_{card_id}")],
            ]
        )
        await message.answer(
            t.MSG_TITLE_UPDATED.format(title=new_title),
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception:
        logger.exception("Failed to update title for card %s", card_id)
        await message.answer(
            t.WARN_TITLE_UPDATE_ERROR,
            reply_markup=get_main_menu(user_id),
            parse_mode=ParseMode.MARKDOWN,
        )


# =============================================================================
# UPDATE CARD DESCRIPTION (Admin only)
# =============================================================================
@router.callback_query(F.data.startswith("updatedesc_"))
async def start_update_description(callback: CallbackQuery, state: FSMContext) -> None:
    """Start the description update workflow."""
    user_id = callback.from_user.id
    t = get_locale(user_id)

    if user_id not in ADMIN_IDS:
        await callback.answer(t.WARN_ACCESS_DENIED, show_alert=True)
        return

    parts = callback.data.split("_")
    if len(parts) < 2:
        return

    card_id = parts[1]

    # Verify card exists
    card = await get_card(card_id)
    if not card:
        await callback.answer(t.WARN_CARD_NOT_FOUND, show_alert=True)
        return

    # Store card info in FSM
    await state.update_data(card_id=card_id, category=card.get("category", "altro"))
    await state.set_state(UpdateCardDescription.write_description)

    # Ask for new description
    kb = get_cancel_button(f"view_{card_id}", user_id)
    current_desc = card.get("description", "N/A")
    await update_message(
        callback,
        t.MSG_UPDATE_DESCRIPTION.format(
            title=card.get("title", "N/A"),
            description=current_desc,
            max_len=MAX_DESCRIPTION_LENGTH,
        ),
        kb,
    )

    fsm_timestamps[user_id] = time.time()
    logger.info("Admin %s started description update for card %s", user_id, card_id)


@router.message(UpdateCardDescription.write_description, F.text)
async def receive_updated_description(message: types.Message, state: FSMContext) -> None:
    """Receive and save the new description."""
    user_id = message.from_user.id
    t = get_locale(user_id)

    if not await check_fsm_timeout(state, user_id):
        await message.answer(
            t.WARN_SESSION_EXPIRED,
            reply_markup=get_main_menu(user_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    new_description = message.text.strip()

    # Validate description length
    if len(new_description) > MAX_DESCRIPTION_LENGTH:
        await message.answer(
            t.WARN_DESCRIPTION_UPDATE_TOO_LONG.format(max_len=MAX_DESCRIPTION_LENGTH, current_len=len(new_description))
        )
        return

    if len(new_description) == 0:
        await message.answer(t.WARN_DESCRIPTION_EMPTY)
        return

    data = await state.get_data()
    card_id = data.get("card_id")
    category = data.get("category", "altro")

    if not card_id:
        await message.answer(t.WARN_MISSING_DATA)
        await state.clear()
        fsm_timestamps.pop(user_id, None)
        return

    try:
        # Update the description in the database
        await update_card_description(int(card_id), new_description, admin_id=user_id)
        logger.info("Admin %s updated description for card %s", user_id, card_id)

        # Clear FSM state
        await state.clear()
        fsm_timestamps.pop(user_id, None)

        # Send confirmation
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [make_button(t.BTN_BACK_TO_CATEGORY, f"cat_{category}")],
                [make_button(t.BTN_VIEW_CARD, f"view_{card_id}")],
            ]
        )
        await message.answer(
            t.MSG_DESCRIPTION_UPDATED,
            reply_markup=kb,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception:
        logger.exception("Failed to update description for card %s", card_id)
        await message.answer(
            t.WARN_DESCRIPTION_UPDATE_ERROR,
            reply_markup=get_main_menu(user_id),
            parse_mode=ParseMode.MARKDOWN,
        )
