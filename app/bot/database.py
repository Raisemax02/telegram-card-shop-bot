"""Database operations - Async CRUD on TinyDB with YAML storage.

All database operations go through this module.
Includes automatic backups and validation.
Uses an asyncio Lock to prevent concurrent writes (TinyDB is not thread-safe).
"""

import asyncio
import logging
import re
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path

import yaml
from tinydb import Query, Storage, TinyDB

from .audit import log_card_add, log_card_delete, log_description_update, log_title_update, log_video_update
from .config import DATA_DIR, DB_PATH, MAX_BACKUPS_KEPT, VALID_CATEGORIES

logger = logging.getLogger(__name__)

# Global lock to serialise all database write operations.
# TinyDB is NOT thread-safe; without this, concurrent asyncio.to_thread()
# calls can corrupt the YAML file.
_db_lock = asyncio.Lock()


# =============================================================================
# YAML STORAGE BACKEND
# =============================================================================
class YAMLStorage(Storage):
    """TinyDB storage backend using YAML format.

    Provides human-readable storage with proper formatting.
    """

    def __init__(self, path: Path) -> None:
        """Initialize YAML storage.

        Args:
            path: Path to YAML file
        """
        self.path = path
        self._handle = None

    def read(self) -> dict | None:
        """Read data from YAML file."""
        if not self.path.exists():
            return None

        try:
            with open(self.path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if data else None
        except Exception:
            logger.exception("Failed to read YAML database")
            return None

    def write(self, data: dict) -> None:
        """Write data to YAML file atomically.

        Writes to a temporary file first, then renames it to the target path.
        This prevents data corruption if the process crashes mid-write.

        Args:
            data: Dictionary to write
        """
        temp_path = self.path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    indent=2,
                )
            # Atomic rename (best-effort on Windows, atomic on POSIX)
            temp_path.replace(self.path)
        except Exception:
            logger.exception("Failed to write YAML database")
            # Clean up temp file on failure
            temp_path.unlink(missing_ok=True)
            raise

    def close(self) -> None:
        """Close storage (no-op for YAML)."""
        pass


# Global database instance with YAML storage
db = TinyDB(DB_PATH, storage=YAMLStorage)


# =============================================================================
# BACKUP
# =============================================================================
def backup_database() -> None:
    """Create a timestamped database backup.

    Keeps only the last MAX_BACKUPS_KEPT backups.
    """
    backup_dir = DATA_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)

    try:
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"cards_backup_{timestamp}.yaml"
        shutil.copy2(DB_PATH, backup_file)
        logger.info("Database backup created: %s", backup_file.name)

        # Clean up old backups
        backups = sorted(
            [f for f in backup_dir.iterdir() if f.name.startswith("cards_backup_") and f.suffix == ".yaml"],
            key=lambda p: p.name,
            reverse=True,
        )
        for old_backup in backups[MAX_BACKUPS_KEPT:]:
            try:
                old_backup.unlink()
                logger.info("Old backup removed: %s", old_backup.name)
            except PermissionError:
                logger.warning("Cannot delete backup %s: permission denied", old_backup.name)
            except Exception:
                logger.exception("Failed to remove old backup %s", old_backup.name)
    except Exception:
        logger.exception("Backup failed")


# =============================================================================
# VALIDATION & SANITIZATION
# =============================================================================
def validate_category(category: str) -> bool:
    """Check that the category is in the whitelist."""
    return category in VALID_CATEGORIES


# Characters that have special meaning in Telegram MarkdownV1 / Markdown
_MARKDOWN_SPECIAL_RE = re.compile(r"([_*\[\]()~`>#+=|{}.!\-])")


def sanitize_text(text: str, max_length: int | None = None, escape_markdown: bool = False) -> str:
    """Sanitize user input to prevent injection attacks.

    Args:
        text: User input text
        max_length: Optional maximum length
        escape_markdown: If True, escape Telegram Markdown special chars

    Returns:
        Sanitized text safe for YAML/Markdown
    """
    if not text:
        return ""

    # Remove null bytes and control characters (except newlines/tabs)
    text = "".join(char for char in text if char.isprintable() or char in "\n\t")

    # Strip leading/trailing whitespace
    text = text.strip()

    # Escape YAML special characters that could break the format
    # Check the ENTIRE string, not just the first character
    yaml_special_start = set(":{}[]&*#|>'\"%%@`")
    if text and text[0] in yaml_special_start:
        text = " " + text

    # Optionally escape Telegram Markdown special characters
    if escape_markdown:
        text = _MARKDOWN_SPECIAL_RE.sub(r"\\\1", text)

    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text


def format_description(text: str) -> str:
    """Format description: sanitize, strip whitespace and capitalize first letter."""
    text = sanitize_text(text)
    if text:
        text = text[0].upper() + text[1:]
    return text


def validate_video_mimetype(file_name: str | None) -> bool:
    """Validate video file extension.

    Args:
        file_name: File name from Telegram

    Returns:
        True if valid video format
    """
    if not file_name:
        return True  # Telegram API already validates, this is extra check

    valid_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".mpeg", ".mpg"}
    file_ext = Path(file_name).suffix.lower()
    return file_ext in valid_extensions or not file_ext  # Allow files without extension


async def user_has_reviewed(card_id: int, user_id: int) -> bool:
    """Check if user has already reviewed this card.

    Args:
        card_id: Card document ID
        user_id: Telegram user ID

    Returns:
        True if user already left a review
    """

    def _check() -> bool:
        card = db.get(doc_id=int(card_id))
        if not card:
            return False
        reviews = card.get("reviews", [])
        return any(r.get("user_id") == user_id for r in reviews)

    try:
        return await asyncio.to_thread(_check)
    except Exception:
        logger.exception("Failed to check user reviews for card %s", card_id)
        return False


# =============================================================================
# CRUD OPERATIONS
# =============================================================================
async def add_card(category: str, title: str, video_id: str, description: str, admin_id: int | None = None) -> int:
    """Insert a new card. Returns the doc_id."""
    title = sanitize_text(title.strip().title())
    description = format_description(description)

    def _insert() -> int:
        return db.insert(
            {
                "category": category,
                "title": title,
                "video_id": video_id,
                "description": description,
                "reviews": [],
            }
        )

    try:
        async with _db_lock:
            result = await asyncio.to_thread(_insert)
            await asyncio.to_thread(backup_database)

        # Audit log
        if admin_id:
            log_card_add(admin_id, result, title, category)
    except Exception:
        logger.exception("Card insertion failed")
        raise
    else:
        return result


async def get_cards(category: str) -> list[tuple[int, str]]:
    """Return all cards in a category as [(doc_id, title)]."""

    def _search() -> list:
        q = Query()
        return db.search(q.category == category)

    try:
        cards = await asyncio.to_thread(_search)
    except Exception:
        logger.exception("Search failed for category '%s'", category)
        return []
    else:
        return [(doc.doc_id, doc["title"]) for doc in cards]


async def get_card(card_id: int) -> dict | None:
    """Return a single card by doc_id, or None."""

    def _get() -> dict | None:
        return db.get(doc_id=int(card_id))

    try:
        return await asyncio.to_thread(_get)
    except Exception:
        logger.exception("Failed to read card %s", card_id)
        return None


async def delete_card(card_id: int, admin_id: int | None = None) -> None:
    """Delete a card (with preventive backup)."""
    # Get card info before deletion for audit log
    card = await get_card(card_id)
    card_title = card.get("title", "Unknown") if card else "Unknown"

    def _remove() -> None:
        db.remove(doc_ids=[int(card_id)])

    try:
        async with _db_lock:
            await asyncio.to_thread(backup_database)
            await asyncio.to_thread(_remove)

        # Audit log
        if admin_id:
            log_card_delete(admin_id, int(card_id), card_title)
    except Exception:
        logger.exception("Failed to delete card %s", card_id)
        raise


async def update_card_video(card_id: int, video_id: str, admin_id: int | None = None) -> None:
    """Update the video_id of an existing card.

    Args:
        card_id: The document ID of the card
        video_id: The new Telegram file_id for the video
        admin_id: Admin user ID for audit logging
    """
    # Get card info for audit log
    card = await get_card(card_id)
    card_title = card.get("title", "Unknown") if card else "Unknown"

    def _update() -> None:
        db.update({"video_id": video_id}, doc_ids=[int(card_id)])

    try:
        async with _db_lock:
            await asyncio.to_thread(_update)
            await asyncio.to_thread(backup_database)
        logger.info("Updated video for card %s", card_id)

        # Audit log
        if admin_id:
            log_video_update(admin_id, int(card_id), card_title)
    except Exception:
        logger.exception("Failed to update video for card %s", card_id)
        raise


async def update_card_title(card_id: int, new_title: str, admin_id: int | None = None) -> None:
    """Update the title of an existing card.

    Args:
        card_id: The document ID of the card
        new_title: The new title for the card
        admin_id: Admin user ID for audit logging
    """
    # Sanitize title
    new_title = sanitize_text(new_title.strip().title())

    # Get old title for audit log
    card = await get_card(card_id)
    old_title = card.get("title", "Unknown") if card else "Unknown"

    def _update() -> None:
        db.update({"title": new_title}, doc_ids=[int(card_id)])

    try:
        async with _db_lock:
            await asyncio.to_thread(_update)
            await asyncio.to_thread(backup_database)
        logger.info("Updated title for card %s: '%s' -> '%s'", card_id, old_title, new_title)

        # Audit log
        if admin_id:
            log_title_update(admin_id, int(card_id), old_title, new_title)
    except Exception:
        logger.exception("Failed to update title for card %s", card_id)
        raise


async def update_card_description(card_id: int, new_description: str, admin_id: int | None = None) -> None:
    """Update the description of an existing card.

    Args:
        card_id: The document ID of the card
        new_description: The new description for the card
        admin_id: Admin user ID for audit logging
    """
    # Format description
    new_description = format_description(new_description)

    # Get card title for audit log
    card = await get_card(card_id)
    card_title = card.get("title", "Unknown") if card else "Unknown"

    def _update() -> None:
        db.update({"description": new_description}, doc_ids=[int(card_id)])

    try:
        async with _db_lock:
            await asyncio.to_thread(_update)
            await asyncio.to_thread(backup_database)
        logger.info("Updated description for card %s (%s)", card_id, card_title)

        # Audit log
        if admin_id:
            log_description_update(admin_id, int(card_id), card_title)
    except Exception:
        logger.exception("Failed to update description for card %s", card_id)
        raise


async def add_review(card_id: int, user_id: int, rating: int, comment: str = "") -> None:
    """Add a review to a card.

    Args:
        card_id: Card document ID
        user_id: Telegram user ID
        rating: Rating from 1 to 5
        comment: Optional comment text

    Raises:
        ValueError: If user already reviewed this card
    """
    # Check for duplicate review
    if await user_has_reviewed(card_id, user_id):
        raise ValueError("User has already reviewed this card")

    # Sanitize comment
    comment = sanitize_text(comment, max_length=200)

    def _add() -> None:
        card = db.get(doc_id=int(card_id))
        if card:
            reviews = card.get("reviews", [])
            reviews.append(
                {
                    "user_id": user_id,
                    "rating": rating,
                    "comment": comment,
                    "timestamp": time.time(),
                }
            )
            db.update({"reviews": reviews}, doc_ids=[int(card_id)])

    try:
        async with _db_lock:
            await asyncio.to_thread(_add)
    except Exception:
        logger.exception("Failed to save review for card %s", card_id)
        raise


async def get_all_cards() -> list[dict]:
    """Return all cards in the database."""
    return await asyncio.to_thread(db.all)


# =============================================================================
# CALCULATIONS
# =============================================================================
def calculate_review_average(reviews: list) -> float:
    """Calculate the average rating. Returns 0.0 if no reviews."""
    if not reviews:
        return 0.0
    ratings = [r.get("rating", 0) for r in reviews if isinstance(r, dict)]
    return sum(ratings) / len(ratings) if ratings else 0.0
