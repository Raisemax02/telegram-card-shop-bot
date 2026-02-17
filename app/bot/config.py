"""
Bot configuration — Environment variables, constants, and paths.

All settings centralized in a single module.
No business logic here: static data only.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# =============================================================================
# PATHS
# =============================================================================
# Navigate from app/bot/config.py -> app/bot/ -> app/ -> root/
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "cards.yaml"

# Welcome image — place your file at data/welcome.jpg
WELCOME_IMAGE_PATH = DATA_DIR / "welcome.jpg"

# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================
load_dotenv(PROJECT_DIR / ".env")

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    sys.exit("ERROR: BOT_TOKEN missing from .env file")

_raw_ids = os.getenv("ADMIN_IDS", "")
try:
    ADMIN_IDS: list[int] = [int(x.strip()) for x in _raw_ids.split(",") if x.strip()]
except ValueError:
    sys.exit("ERROR: ADMIN_IDS invalid. Use comma-separated integers.")

if not ADMIN_IDS:
    sys.exit("ERROR: No ADMIN_IDS configured. At least one admin is required.")

# =============================================================================
# CONSTANTS
# =============================================================================
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
AUTO_DELETE_VIDEO_SECONDS = 60
WARNING_MESSAGE_DURATION = 3
MAX_BUTTON_LENGTH = 30
RATE_LIMIT_WINDOW = 5
FSM_TIMEOUT_SECONDS = 300
MAX_VIDEO_SIZE_MB = 50
MAX_BACKUPS_KEPT = 5
MAX_REVIEWS_PER_PAGE = 5
CARDS_PER_PAGE = 8  # Maximum cards to show per page in category view

# =============================================================================
# CATEGORIES
# =============================================================================
VALID_CATEGORIES: set[str] = {"yugioh", "pokemon", "magic", "altro"}

CATEGORY_NAMES: dict[str, str] = {
    "yugioh": "🐉 Yu-Gi-Oh!",
    "pokemon": "⚡ Pokémon",
    "magic": "🔮 Magic",
    "altro": "🔧 Altro",
}
