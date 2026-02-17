"""
Internationalization (i18n) system — Locale manager and user preferences.

Manages language preferences per user and provides access to localized strings.
Default language: English (en).
User preferences are persisted in a JSON file so they survive bot restarts.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .en import Locale

logger = logging.getLogger(__name__)

# Persistence file for user language choices
_PREFS_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "user_languages.json"

# In-memory storage for user language preferences
_user_languages: dict[int, str] = {}

# Available locales
_locales: dict[str, Locale] = {}


def _load_user_languages() -> None:
    """Load persisted user language preferences from disk."""
    global _user_languages  # noqa: PLW0603
    if not _PREFS_PATH.exists():
        return
    try:
        with open(_PREFS_PATH, encoding="utf-8") as f:
            raw = json.load(f)
        # JSON keys are always strings; convert back to int
        _user_languages = {int(k): v for k, v in raw.items() if isinstance(v, str)}
        logger.info("Loaded language preferences for %d user(s)", len(_user_languages))
    except Exception:
        logger.exception("Failed to load user language preferences")


def _save_user_languages() -> None:
    """Persist current user language preferences to disk."""
    try:
        _PREFS_PATH.parent.mkdir(exist_ok=True)
        # Write atomically via temp file
        temp = _PREFS_PATH.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in _user_languages.items()}, f, indent=2)
        temp.replace(_PREFS_PATH)
    except Exception:
        logger.exception("Failed to save user language preferences")


def register_locale(locale: Locale) -> None:
    """Register a locale module."""
    _locales[locale.LANG_CODE] = locale
    logger.debug("Registered locale: %s", locale.LANG_CODE)


def get_locale(user_id: int | None = None) -> Locale:
    """Get the locale for a user. Returns default (en) if not set."""
    lang_code = "en" if user_id is None else _user_languages.get(user_id, "en")
    return _locales.get(lang_code, _locales["en"])


def set_user_language(user_id: int, lang_code: str) -> bool:
    """Set the preferred language for a user. Returns True if successful.

    Persists the change to disk so it survives bot restarts.
    """
    if lang_code not in _locales:
        logger.warning("Attempted to set unknown language: %s", lang_code)
        return False

    _user_languages[user_id] = lang_code
    _save_user_languages()
    logger.info("User %s language set to %s", user_id, lang_code)
    return True


def get_available_languages() -> dict[str, str]:
    """Return a dict of {lang_code: lang_name} for all available languages."""
    return {code: locale.LANG_NAME for code, locale in _locales.items()}


def initialize_locales() -> None:
    """Initialize all available locales and load persisted user preferences."""
    from . import en, it

    register_locale(en)
    register_locale(it)
    _load_user_languages()
    logger.info("Initialized %d locale(s): %s", len(_locales), ", ".join(_locales.keys()))
