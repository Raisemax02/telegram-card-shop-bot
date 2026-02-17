"""English (en) locale — UI strings."""

from __future__ import annotations

LANG_CODE = "en"
LANG_NAME = "English"
FLAG = "🇬🇧"

# --- Language Selection -------------------------------------------------------
MSG_SELECT_LANGUAGE = "🌍 **Select your language / Seleziona la lingua:**"
MSG_LANGUAGE_CHANGED = "✅ Language set to English"

# --- Main Menu ----------------------------------------------------------------
MSG_START = (
    "👋 **Welcome to the Collectible Card Shop!**\n\n"
    "🃏 Browse our categories to see available cards "
    "and their condition via video.\n\n"
    "Choose an option below ⬇️"
)

MSG_CATEGORIES_MENU = "📂 **Categories**\n\nChoose a category to browse cards:"

# --- Info & Contacts ----------------------------------------------------------
MSG_INFO = (
    "🏢 **Shop Info**\n\n"
    "📍 Open Mon-Sat, 9:00 AM – 7:00 PM\n"
    "🃏 Yu-Gi-Oh!, Pokémon, Magic, and more\n\n"
    "Use the buttons below to navigate ⬇️"
)

MSG_CONTACTS = (
    "📞 **Contact Us**\n\n📱 Phone: 0123-456789\n📧 Email: info@shop.com\n\nUse the buttons below to navigate ⬇️"
)

# --- Reviews ------------------------------------------------------------------
MSG_REVIEWS_TITLE = "⭐ **Card Reviews**\n\n"
ROW_CARD_REVIEW = "🏷 {title}: ⭐ {average:.1f} ({count} reviews)\n"
ROW_OVERALL_RATING = "\n📊 **Overall Rating:** ⭐ {average:.1f} ({total} total reviews)"
NO_REVIEWS = "No reviews yet."
ERR_REVIEWS_LOAD = "⚠️ Error loading reviews."

MSG_START_REVIEW = "⭐ **Review for {title}**\n\nChoose a rating from 1 to 5 stars:"
MSG_WRITE_COMMENT = "⭐ **Rating:** {rating} stars for {title}\n\nWrite a comment (optional, max 200 characters):"
CONFIRM_REVIEW = "✅ Review saved! Thank you for your feedback. ⭐"
MSG_REVIEW_SAVED = "✅ Review saved!"
ERR_SAVE_REVIEW = "⚠️ Error saving review."

# --- Admin Panel --------------------------------------------------------------
MSG_ADMIN_PANEL = "🔐 **Admin Panel**\n\nChoose the category to manage:"

# --- FSM: Card Upload ---------------------------------------------------------
MSG_WRITE_TITLE = "📝 Adding to **{cat_name}**\n\nWrite the card **NAME/TITLE**:\n_(max {max_len} characters)_"
MSG_TITLE_OK = "✅ Title: **{title}**\n\n🎥 **Now send the VIDEO** of the card."
MSG_VIDEO_OK = "✅ Video received!\n\n📝 **Now write the Description and Price**:\n\n_(max {max_len} characters)_"
MSG_CARD_PUBLISHED = "✅ **Card published successfully!**"
MSG_CARD_DELETED = "🗑 Card deleted!"

# --- Delete Confirmation ------------------------------------------------------
MSG_CONFIRM_DELETE = "🗑 **Confirm Deletion**\n\nDelete card **{title}**?\n\n⚠️ This action is **irreversible**."

# --- Category -----------------------------------------------------------------
MSG_CATEGORY = "📂 **{cat_name}**"
NO_CARDS = "\n\n📭 No cards available at the moment."

# --- Warnings / Errors --------------------------------------------------------
WARN_SESSION_EXPIRED = "⏰ **Session expired due to inactivity.** Please start over."
WARN_TEXT_REQUIRED = "⚠️ Please write a text for the title, don't send files."
WARN_TITLE_TOO_LONG = "⚠️ Title too long. Maximum {max} characters."
WARN_VIDEO_REQUIRED = "⚠️ Please send a **video**, not a text message or other file."
WARN_VIDEO_TOO_LARGE = "⚠️ Video too large. Maximum {max} MB."
WARN_DESCRIPTION_REQUIRED = "⚠️ Please write a text description."
WARN_DESCRIPTION_TOO_LONG = "⚠️ Description too long. Maximum {max} characters."
WARN_MISSING_DATA = "⚠️ Error: missing data. Please start over."
WARN_INVALID_CATEGORY = "⚠️ Invalid category."
WARN_ACCESS_DENIED = "⛔️ Access denied"
WARN_CARD_NOT_FOUND = "Card not found."
WARN_VIDEO_UNAVAILABLE = "⚠️ Video unavailable."
WARN_SAVE_ERROR = "⚠️ Error during save. Please try again."
WARN_DELETE_ERROR = "⚠️ Error during deletion"
WARN_COMMENT_TOO_LONG = "Comment too long. Max 200 characters."
WARN_WRITE_COMMENT = "Write a comment or use the 'Skip comment' button."
WARN_SPAM = "⛔️ **Please use only the menu buttons!**"
WARN_ALREADY_REVIEWED = "⚠️ You have already reviewed this card."
WARN_INVALID_VIDEO_FORMAT = "⚠️ Invalid video format. Use: MP4, MOV, AVI, MKV, WebM."
WARN_REVIEW_RATE_LIMIT = "⚠️ You've reached the review limit. Try again in {minutes} minutes."

# --- Labels -------------------------------------------------------------------
LBL_RATING = "Rating"
LBL_REVIEWS = "reviews"

# --- Button Labels ------------------------------------------------------------
BTN_MENU_CARDS = "📂  Card Menu"
BTN_REVIEWS = "⭐  Reviews"
BTN_INFO = "ℹ️ Info"
BTN_CONTACTS = "📞 Contact"
BTN_BACK = "🔙 Back"
BTN_CANCEL = "❌ Cancel"
BTN_ADD_CARD = "ADD CARD"
BTN_SKIP_COMMENT = "Skip comment"
BTN_DELETE = "🗑"
BTN_YES_DELETE = "Yes, delete"
BTN_LEAVE_REVIEW = "Leave Review"
BTN_LANGUAGE = "🌍 Language"
BTN_CATEGORIES_MENU = "Category Menu"
BTN_BACK_TO_CAT = "Back to {cat_name}"

# --- Pagination ---------------------------------------------------------------
BTN_PREVIOUS = "◀️ Previous"
BTN_NEXT = "Next ▶️"
LBL_PAGE = "Page"

# --- Admin: Update Video ------------------------------------------------------
MSG_UPDATE_VIDEO = (
    "📹 **Update Video**\n\n"
    "🏷 **Card:** {title}\n\n"
    "Send the new video for this card.\n\n"
    "⚠️ The previous video will be replaced."
)
MSG_VIDEO_UPDATED = "✅ **Video updated successfully!**\n\nThe new video has been saved."
WARN_VIDEO_UPDATE_ERROR = "❌ Error updating video. Please try again later."

# --- Admin: Update Title ------------------------------------------------------
MSG_UPDATE_TITLE = (
    "✏️ **Edit Title**\n\n"
    "📝 **Current Title:** {title}\n\n"
    "Send the new title for this card.\n\n"
    "⚠️ Max {max_len} characters."
)
MSG_TITLE_UPDATED = "✅ **Title updated successfully!**\n\n📝 **New Title:** {title}"
WARN_TITLE_UPDATE_ERROR = "❌ Error updating title. Please try again later."
WARN_TITLE_EMPTY = "⚠️ The title cannot be empty."
WARN_TITLE_UPDATE_TOO_LONG = "⚠️ Title too long. Max {max_len} characters.\n\nCurrent length: {current_len} characters."

# --- Admin: Update Description ------------------------------------------------
MSG_UPDATE_DESCRIPTION = (
    "📝 **Edit Description**\n\n"
    "🏷 **Card:** {title}\n\n"
    "📄 **Current Description:**\n{description}\n\n"
    "Send the new description for this card.\n\n"
    "⚠️ Max {max_len} characters."
)
MSG_DESCRIPTION_UPDATED = "✅ **Description updated successfully!**\n\nThe new description has been saved."
WARN_DESCRIPTION_UPDATE_ERROR = "❌ Error updating description. Please try again later."
WARN_DESCRIPTION_EMPTY = "⚠️ The description cannot be empty."
WARN_DESCRIPTION_UPDATE_TOO_LONG = (
    "⚠️ Description too long. Max {max_len} characters.\n\nCurrent length: {current_len} characters."
)

# --- Admin: Card View Buttons -------------------------------------------------
BTN_EDIT_TITLE = "✏️ Title"
BTN_EDIT_DESCRIPTION = "📝 Description"
BTN_UPDATE_VIDEO = "📹 Update Video"
BTN_BACK_TO_CATEGORY = "🔙 Back to Category"
BTN_VIEW_CARD = "👁️ View Card"
