"""Audit logging — Track admin actions for security and compliance.

All administrative actions are logged with timestamp, user ID, and action details.
"""

import logging
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create a separate logger for audit events
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
audit_logger.propagate = False  # Don't propagate to root logger

# Audit log file path
AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent.parent / "logs" / "audit.log"
AUDIT_LOG_PATH.parent.mkdir(exist_ok=True)

# Rotating file handler for audit log (50 MB, keep 20 backups for compliance)
audit_handler = RotatingFileHandler(
    AUDIT_LOG_PATH,
    maxBytes=50 * 1024 * 1024,
    backupCount=20,
    encoding="utf-8",
)

# Audit log format: timestamp | user_id | action | details
audit_formatter = logging.Formatter(
    "%(asctime)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)


def log_admin_action(user_id: int, action: str, details: str = "") -> None:
    """Log an admin action to the audit log.

    Args:
        user_id: Telegram user ID of the admin
        action: Action performed (e.g., "CARD_ADD", "CARD_DELETE", "VIDEO_UPDATE")
        details: Additional details about the action
    """
    timestamp = datetime.now(tz=UTC).isoformat()
    audit_logger.info(
        "user_id=%s | action=%s | details=%s | timestamp=%s",
        user_id,
        action,
        details,
        timestamp,
    )


def log_card_add(user_id: int, card_id: int, title: str, category: str) -> None:
    """Log card creation."""
    log_admin_action(
        user_id,
        "CARD_ADD",
        f"card_id={card_id} | title={title[:50]} | category={category}",
    )


def log_card_delete(user_id: int, card_id: int, title: str) -> None:
    """Log card deletion."""
    log_admin_action(
        user_id,
        "CARD_DELETE",
        f"card_id={card_id} | title={title[:50]}",
    )


def log_video_update(user_id: int, card_id: int, title: str) -> None:
    """Log video update."""
    log_admin_action(
        user_id,
        "VIDEO_UPDATE",
        f"card_id={card_id} | title={title[:50]}",
    )


def log_title_update(user_id: int, card_id: int, old_title: str, new_title: str) -> None:
    """Log title update."""
    log_admin_action(
        user_id,
        "TITLE_UPDATE",
        f"card_id={card_id} | old_title={old_title[:40]} | new_title={new_title[:40]}",
    )


def log_description_update(user_id: int, card_id: int, title: str) -> None:
    """Log description update."""
    log_admin_action(
        user_id,
        "DESCRIPTION_UPDATE",
        f"card_id={card_id} | title={title[:50]}",
    )


def log_security_event(event_type: str, user_id: int, details: str = "") -> None:
    """Log security-related events.

    Args:
        event_type: Event type (e.g., "RATE_LIMIT", "ACCESS_DENIED", "DUPLICATE_REVIEW")
        user_id: Telegram user ID
        details: Additional event details
    """
    log_admin_action(user_id, f"SECURITY_{event_type}", details)
