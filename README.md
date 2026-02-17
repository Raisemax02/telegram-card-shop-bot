# 🤖 Telegram Bot - Collectible Card Shop

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-blue.svg)](https://docs.aiogram.dev/)
[![Ruff](https://img.shields.io/badge/Linter-Ruff-black.svg)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](https://opensource.org/licenses/)

Professional Telegram bot for managing a collectible card shop (Yu-Gi-Oh!, Pokémon, Magic, etc.) with multilingual support, review system, admin panel, and advanced security features.

---

## 📖 Table of Contents

- [For End Users](#-end-user-guide)
- [For Developers](#-developer-guide)
- [Features](#-features)
- [Security](#-security--compliance)
- [Quick Start](#-quick-start)
- [Deployment](#-deployment)
- [API Reference](#-api-reference)

---

## 👥 End User Guide

### How to Use the Bot

#### 1. **Start the Bot**

Search for the bot on Telegram and send `/start`

<details>
<summary>📸 Main Menu Screenshots</summary>

```text
👋 Welcome to the Collectible Card Shop!

🃏 Browse our categories to see the available cards
and their condition via video.

Choose an option below ⬇️

┌─────────────────────┐
│  📂  Card Menu      │
├─────────────────────┤
│  ⭐  Reviews        │
├─────────────────────┤
│  ℹ️ Info │ 📞 Contacts │
├─────────────────────┤
│    🌍 Language      │
└─────────────────────┘
```

</details>

#### 2. **Browse Categories**

Click on **📂 Card Menu** to see the available categories:

- 🐉 **Yu-Gi-Oh!** - Yu-Gi-Oh! trading cards
- ⚡ **Pokémon** - Pokémon TCG cards
- 🔮 **Magic** - Magic: The Gathering
- 🔧 **Other** - Other collectible cards

#### 3. **View Cards**

Each card displays:

- 🎥 **Video** of the card (condition, authenticity)
- 📝 **Description** and price
- ⭐ **Average rating** from reviews
- 💬 **Number of reviews**

> ⚠️ **Privacy Note**: Videos are automatically deleted after 60 seconds

#### 4. **Leave a Review**

1. Click on **⭐ Leave Review**
2. Choose a rating from 1 to 5 stars
3. Write a comment (optional, max 200 characters)
4. Confirm

**Limitations:**

- ✅ You can review each card **only once**
- ✅ Maximum **3 reviews per hour** (anti-spam)

#### 5. **Change Language**

The bot supports:

- 🇮🇹 **Italiano**
- 🇬🇧 **English**

Click on **🌍 Language** in the main menu to switch.

---

## 💻 Developer Guide

### Project Architecture

```text
BOT_TELEGRAM/
├── app/
│   ├── main.py                 # 🚀 Bot entry point (graceful shutdown)
│   └── bot/
│       ├── config.py           # ⚙️  Configuration and environment variables
│       ├── logger.py           # 📝 Logging with rotation + LOG_LEVEL env
│       ├── database.py         # 💾 TinyDB + atomic YAML + asyncio.Lock
│       ├── keyboards.py        # ⌨️  Uniform inline keyboards
│       ├── audit.py            # 🔍 Audit logging (50 MB, 20 backups)
│       │
│       ├── i18n/               # 🌍 Internationalization system
│       │   ├── __init__.py
│       │   ├── locale.py       # Language preference manager (persisted to disk)
│       │   ├── en.py           # English strings
│       │   └── it.py           # Italian strings
│       │
│       └── handlers/           # 🎯 Modular Telegram handlers
│           ├── __init__.py     # Router registration
│           ├── states.py       # FSM state definitions
│           ├── helpers.py      # Utilities + safe_callback + task tracking
│           ├── commands.py     # /start, /admin commands
│           ├── navigation.py   # Menu navigation
│           ├── cards.py        # Card CRUD + pagination (full i18n)
│           ├── reviews.py      # Review workflow
│           ├── language.py     # Language selection (with fallback)
│           └── antispam.py     # Unsolicited message blocking
│
├── data/
│   ├── cards.yaml              # 📊 Main database (human-readable)
│   ├── user_languages.json     # 🌍 User language preferences (persisted)
│   ├── welcome.jpg             # 🖼️  Welcome image
│   └── backups/                # 💾 Automatic backups (last 5)
│
├── logs/
│   ├── bot.log                 # 📋 Application log (5 MB, 3 backups)
│   └── audit.log               # 🔐 Admin action log (50 MB, 20 backups)
│
├── tools/
│   ├── docker-build-run.ps1    # 🐳 Docker management
│   └── maintenance.ps1         # 🛠️  Maintenance utilities
│
├── .env                        # 🔒 Environment variables (DO NOT commit!)
├── .env.example                # 📄 Configuration template
├── Dockerfile                  # 🐳 Multi-stage build + advanced healthcheck
├── docker-compose.yml          # 🐳 Container orchestration
├── pyproject.toml              # 📦 Project metadata (PEP 621)
└── README.md                   # 📖 This guide
```

---

## 🌟 Features

### For Users

- ✅ **Card Catalog** with demonstration videos
- ✅ **Review System** with ratings and comments
- ✅ **Multilingual Support** (Italian, English)
- ✅ **Intuitive Interface** with uniform buttons
- ✅ **Privacy** - Videos auto-deleted after 60 seconds
- ✅ **Anti-Spam** - Message rate limiting

### For Administrators

- ✅ **Add/Delete Cards** via FSM workflow
- ✅ **Update Video** for existing cards
- ✅ **Edit Title and Description** for existing cards
- ✅ **Category Management** (Yu-Gi-Oh!, Pokémon, Magic, Other)
- ✅ **Automatic Pagination** (8 cards per page)
- ✅ **Session Timeout** FSM (5 minutes of inactivity)
- ✅ **Automatic Backups** on every modification (atomic writes)
- ✅ **Multilingual Admin Panel** (all admin messages are localized)

### Technical

- ✅ **Async/Await** - Optimal performance
- ✅ **Type Hints** - Complete for type safety
- ✅ **Ruff Compliance** - PEP 8, import sorting, security checks
- ✅ **Docker Ready** - Optimized multi-stage build
- ✅ **YAML Storage** - Human-readable database with atomic writes
- ✅ **Thread Safety** - `asyncio.Lock` on all DB write operations
- ✅ **Graceful Shutdown** - Clean cleanup on SIGTERM/SIGINT
- ✅ **Safe Callbacks** - Decorator for error handling in callback handlers
- ✅ **Task Tracking** - Video deletion task monitoring
- ✅ **Rotating Logs** - Automatic size management
- ✅ **Health Checks** - Docker container monitoring (log activity check)
- ✅ **Language Persistence** - Language preferences saved to disk
- ✅ **Configurable Logging** - Log level configurable via environment variable

---

## 🔒 Security & Compliance

### Implemented Security Features

#### 1. **Input Sanitization** 🛡️

**Protection against:**

- YAML Injection
- Null byte injection
- Buffer overflow
- Dangerous control characters

**Implementation:**

```python
# app/bot/database.py
import re

_MARKDOWN_SPECIAL_RE = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")

def sanitize_text(
    text: str,
    max_length: int | None = None,
    escape_markdown: bool = False,
) -> str:
    """Remove dangerous characters and limit length."""
    # Remove null bytes and control characters
    text = "".join(char for char in text if char.isprintable() or char in "\n\t")

    # Escape YAML special characters (checks the entire string)
    yaml_special_chars = {":", "{", "}", "[", "]", "&", "*", "#", "|", ">", "'", '"', "%", "@", "`"}
    if any(ch in yaml_special_chars for ch in text):
        text = text.replace("'", "''")  # YAML quote escape

    # Optional Markdown V2 escape for Telegram
    if escape_markdown:
        text = _MARKDOWN_SPECIAL_RE.sub(r"\\\1", text)

    # Limit length
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text
```

**v1.2.0 Improvements:**

- Checks YAML characters across the **entire string**, not just the first character
- Optional **Markdown V2 escape** support (Telegram MarkdownV2)
- Pre-compiled regex for performance

**Applied to:**

- Card titles
- Card descriptions
- Review comments

---

#### 2. **Duplicate Review Prevention** 🚫

**Protection against:**

- Review spam
- Rating manipulation
- Review system abuse

**Implementation:**

```python
# app/bot/database.py
async def user_has_reviewed(card_id: int, user_id: int) -> bool:
    """Check if user has already reviewed the card"""
    card = db.get(doc_id=int(card_id))
    if not card:
        return False
    reviews = card.get("reviews", [])
    return any(r.get("user_id") == user_id for r in reviews)

# app/bot/handlers/reviews.py
if await user_has_reviewed(int(card_id), user_id):
    await callback.answer("⚠️ You have already left a review", show_alert=True)
    return
```

**Behavior:**

- First review: ✅ Accepted
- Duplicate attempt: ❌ Blocked with clear message
- Security log: 📝 Event recorded in `audit.log`

---

#### 3. **Video Format Validation** 📹

**Protection against:**

- Malicious file uploads
- Disguised executables
- Script injection

**Implementation:**

```python
# app/bot/database.py
def validate_video_mimetype(file_name: str | None) -> bool:
    """Validate video file extension"""
    if not file_name:
        return True  # Telegram API already validates

    valid_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".mpeg", ".mpg"}
    file_ext = Path(file_name).suffix.lower()
    return file_ext in valid_extensions or not file_ext
```

**Accepted Formats:**

- ✅ MP4, MOV, AVI, MKV
- ✅ WebM, FLV, MPEG, MPG
- ❌ PDF, EXE, ZIP, JPG, PNG

---

#### 4. **Review Rate Limiting** ⏱️

**Protection against:**

- Review spam
- System flooding
- Resource abuse

**Implementation:**

```python
# app/bot/handlers/helpers.py
RATE_LIMIT_MAX_MESSAGES = 5      # Max messages per window
REVIEW_RATE_LIMIT_MAX = 3        # Max reviews per user
REVIEW_RATE_LIMIT_WINDOW = 3600  # Time window (1 hour)

def check_rate_limit(user_id: int) -> bool:
    """Generic message rate limit (N messages per window)."""
    now = time.time()
    timestamps = rate_limit_registry[user_id]
    timestamps[:] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
    if len(timestamps) >= RATE_LIMIT_MAX_MESSAGES:
        return False
    timestamps.append(now)
    return True

def check_review_rate_limit(user_id: int) -> tuple[bool, int]:
    """Check review rate limit"""
    now = time.time()
    timestamps = review_rate_limit_registry[user_id]
    timestamps[:] = [t for t in timestamps if now - t < REVIEW_RATE_LIMIT_WINDOW]
    if len(timestamps) >= REVIEW_RATE_LIMIT_MAX:
        oldest = min(timestamps)
        remaining = int(REVIEW_RATE_LIMIT_WINDOW - (now - oldest))
        return False, remaining
    timestamps.append(now)
    return True, 0
```

**Limits:**

- Maximum **5 messages** per time window (generic rate limit)
- Maximum **3 reviews per hour** per user
- Clear message: "⚠️ Try again in X minutes"
- Automatic reset after 1 hour

---

#### 5. **Audit Logging** 📊

Complete tracking of administrative actions for compliance and security.

**File:** `logs/audit.log`  
**Format:** `timestamp | user_id=XXX | action=ACTION | details=... | timestamp=ISO8601`

**Tracked Events:**

| Action             | Code                        | Recorded Details           |
| ------------------ | --------------------------- | -------------------------- |
| Card creation      | `CARD_ADD`                  | card_id, title, category   |
| Card deletion      | `CARD_DELETE`               | card_id, title             |
| Video update       | `VIDEO_UPDATE`              | card_id, title             |
| Rate limit applied | `SECURITY_RATE_LIMIT`       | user_id, seconds remaining |
| Duplicate review   | `SECURITY_DUPLICATE_REVIEW` | user_id, card_id           |

**Log Example:**

```text
2026-02-15 16:30:45 | user_id=376115091 | action=CARD_ADD | details=card_id=8 | title=Blue-Eyes White Dragon | category=yugioh | timestamp=2026-02-15T16:30:45+00:00
2026-02-15 16:35:12 | user_id=999999999 | action=SECURITY_RATE_LIMIT | details=review_attempt | remaining=3542s | timestamp=2026-02-15T16:35:12+00:00
```

**Configuration:**

- Automatic rotation at **50 MB**
- Last **20 backups** retained
- UTF-8 encoding
- Not propagated to main log

---

#### 6. **List Pagination** 📄

**Protection against:**

- Telegram messages too long
- Telegram API timeouts
- Poor user experience

**Implementation:**

```python
# app/bot/config.py
CARDS_PER_PAGE = 8  # Maximum cards per page

# app/bot/handlers/cards.py
total_pages = (total_cards + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE
start_idx = (page - 1) * CARDS_PER_PAGE
end_idx = start_idx + CARDS_PER_PAGE
cards_page = all_cards[start_idx:end_idx]
```

**Navigation:**

- ◀️ **Previous** (if page > 1)
- ▶️ **Next** (if page < total)
- Indicator: "📄 Page 2/5"

---

### Standards Compliance

| Standard                  | Description             | Compliance                         |
| ------------------------- | ----------------------- | ---------------------------------- |
| **PEP 8**                 | Python style guide      | ✅ Ruff enforced                   |
| **PEP 517/518**           | Build system            | ✅ pyproject.toml                  |
| **PEP 621**               | Project metadata        | ✅ pyproject.toml                  |
| **PEP 440**               | Versioning              | ✅ Semantic versioning             |
| **OWASP Top 10**          | Security best practices | ✅ Input validation, rate limiting |
| **Docker Best Practices** | Container security      | ✅ Non-root user, multi-stage      |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (recommended 3.13)
- **Git** to clone the repository
- **Docker** (optional, for containerized deployment)

### Local Setup (Development)

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd BOT_TELEGRAM
```

#### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -e .
```

This installs:

- `aiogram` - Telegram bot framework
- `tinydb` - Embedded database
- `pyyaml` - YAML parser
- `python-dotenv` - Environment variable management
- `cryptography` - Cryptography support

#### 4. Configure Environment Variables

Copy the template and edit with your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Get the token from @BotFather on Telegram
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567

# Get your user ID from @userinfobot
ADMIN_IDS=123456789,987654321
```

**How to get the values:**

1. **BOT_TOKEN:**
   - Open [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` and follow the instructions
   - Copy the received token

2. **ADMIN_IDS:**
   - Open [@userinfobot](https://t.me/userinfobot) on Telegram
   - Send `/start`
   - Copy your User ID
   - For multiple admins: `123456789,987654321,555555555`

#### 5. (Optional) Add Welcome Image

Place a JPG image at `data/welcome.jpg` to customize the welcome message.

#### 6. Start the Bot

```bash
python app/main.py
```

Expected output:

```text
2026-02-15 17:00:00 | INFO     | __main__ | Bot started
2026-02-15 17:00:00 | INFO     | __main__ | Active admins: 1
2026-02-15 17:00:00 | INFO     | __main__ | Categories: Yu-Gi-Oh!, Pokémon, Magic, Altro
2026-02-15 17:00:00 | INFO     | __main__ | Database: C:\...\data\cards.yaml
```

#### 7. Test the Bot

Open Telegram and search for your bot, then send `/start`

---

### VS Code Setup (Debug)

#### 1. Open the Project

```bash
code .
```

#### 2. Press F5 to Debug

The configuration is already set up in `.vscode/launch.json`:

- Breakpoints supported
- Hot reload enabled
- Integrated console

---

## 🐳 Deployment

### Docker Deployment (Recommended)

#### Why Docker?

- ✅ Isolated and reproducible environment
- ✅ No Python installation required on server
- ✅ Automatic dependency management
- ✅ Built-in health checks
- ✅ Configurable resource limits

#### Build and Start

##### Method 1: Docker Compose (Recommended)

```bash
# Build and start in background
docker-compose up --build -d

# View logs in real time
docker-compose logs -f bot

# Stop the container
docker-compose down
```

##### Method 2: PowerShell Script (Windows)

```powershell
# Build and run
.\tools\docker-build-run.ps1 -Action rebuild

# Build only
.\tools\docker-build-run.ps1 -Action build

# Start only
.\tools\docker-build-run.ps1 -Action run

# View logs
.\tools\docker-build-run.ps1 -Action logs

# Container status
.\tools\docker-build-run.ps1 -Action status

# Stop container
.\tools\docker-build-run.ps1 -Action stop
```

#### Verify Deployment

```bash
# Check running containers
docker ps

# Expected output:
# CONTAINER ID   IMAGE             STATUS         PORTS   NAMES
# abc123def456   bot_telegram:latest   Up 2 minutes           telegram-bot

# Application logs
docker-compose logs bot

# Resource statistics
docker stats telegram-bot
```

#### Resource Limits (docker-compose.yml)

```yaml
deploy:
  resources:
    limits:
      cpus: "0.50" # Max 50% CPU
      memory: 256M # Max 256 MB RAM
```

---

### Traditional Deployment (Linux Server)

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12+
sudo apt install python3.12 python3.12-venv -y

# Clone repository
git clone <repository-url>
cd BOT_TELEGRAM
```

#### 2. Configure Systemd Service

Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Card Shop Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/BOT_TELEGRAM
Environment="PATH=/home/botuser/BOT_TELEGRAM/.venv/bin"
ExecStart=/home/botuser/BOT_TELEGRAM/.venv/bin/python app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot

# Check status
sudo systemctl status telegram-bot

# View logs
sudo journalctl -u telegram-bot -f
```

---

## 🛠️ Maintenance

### Maintenance Script (PowerShell)

#### Health Check

```powershell
.\tools\maintenance.ps1 -Action health
```

Output:

```text
[HEALTH] Bot Health Check
=========================
[OK] Database: 15.32 KB
[OK] Backups: 5 file(s)
[OK] Logs: 2 file(s), 125.45 KB
[OK] Docker: Up 3 hours
[OK] .env file present
```

#### Manual Backup

```powershell
.\tools\maintenance.ps1 -Action backup
```

Creates a timestamped backup in `data/backups/`

#### Cleanup

```powershell
.\tools\maintenance.ps1 -Action cleanup
```

Removes:

- Old backups (beyond the 5 most recent)
- `__pycache__` directories
- `.egg-info` directories

#### Database Info

```powershell
.\tools\maintenance.ps1 -Action db-info
```

Output:

```text
[DATABASE] Database Information
===============================
[INFO] Total cards: 7
  [1] Blue-Eyes White Dragon (yugioh) - 2 review(s)
  [2] Charizard Holographic (pokemon) - 1 review(s)
  ...
```

#### Reset Logs

```powershell
.\tools\maintenance.ps1 -Action reset-logs
```

Deletes all `.log` files (useful for testing)

---

### Monitoring and Logs

#### Log Files

| File             | Purpose                        | Rotation | Backups |
| ---------------- | ------------------------------ | -------- | ------- |
| `logs/bot.log`   | General application log        | 5 MB     | 3       |
| `logs/audit.log` | Admin actions and security log | 50 MB    | 20      |

#### View Logs in Real Time

```bash
# Linux/Mac
tail -f logs/bot.log
tail -f logs/audit.log

# Windows PowerShell
Get-Content logs\bot.log -Wait -Tail 50
```

#### Audit Log Analysis

```bash
# All admin actions
grep "CARD_ADD\|CARD_DELETE\|VIDEO_UPDATE" logs/audit.log

# Security events
grep "SECURITY_" logs/audit.log

# Actions by a specific admin
grep "user_id=376115091" logs/audit.log
```

---

## 📊 Database

### YAML Structure

```yaml
_default:
  '1':                          # Auto-incremental ID
    category: yugioh            # Category (yugioh, pokemon, magic, altro)
    title: Blue-Eyes White Dragon
    video_id: BAACAgQAAxkBAAO...  # Telegram file_id
    description: Rare card in excellent condition. Price: €50
    reviews:
      - user_id: 123456789
        rating: 5               # 1-5 stars
        comment: Perfect card!
        timestamp: 1739577600.0 # Unix timestamp
      - user_id: 987654321
        rating: 4
        comment: Good card
        timestamp: 1739580000.0
```

### Database Operations

#### Thread Safety & Atomic Writes

The database uses an `asyncio.Lock` to ensure thread safety on all concurrent write operations.
YAML writes are **atomic**: the file is first written to a temporary file (`.tmp`) and then renamed with `os.replace()`, preventing data corruption in case of a crash.

```python
# All write operations are protected by lock
async with _db_lock:
    db.update({"video_id": new_video_id}, doc_ids=[card_id])
```

#### Automatic Backups

Created automatically on:

- ✅ Card addition
- ✅ Card deletion
- ✅ Video update
- ✅ Title/description update

**Location:** `data/backups/cards_backup_YYYYMMDD_HHMMSS.yaml`  
**Retention:** Last 5 backups  
**Errors:** Handled individually per file (a cleanup error does not block operations)

#### Restore from Backup

```bash
# Find desired backup
ls data/backups/

# Restore (overwrites current database!)
cp data/backups/cards_backup_20260215_170000.yaml data/cards.yaml

# Restart bot
python app/main.py  # or restart Docker
```

#### Manual Editing

The database is in human-readable YAML format:

```bash
# Open with editor
nano data/cards.yaml  # Linux
notepad data\cards.yaml  # Windows
```

⚠️ **Warning:**

- Follow YAML syntax strictly
- Always use **spaces** (no tabs!)
- Maintain correct indentation
- Validate with a YAML parser before saving

```python
# Test YAML validity
import yaml
with open('data/cards.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
    print("✅ Valid YAML")
```

---

## 🌍 Internationalization (i18n)

### Supported Languages

- 🇮🇹 **Italiano** - Default language
- 🇬🇧 **English** - Secondary language

### Adding a New Language

#### 1. Create Locale File

Create `app/bot/i18n/LANG_CODE.py` (e.g., `es.py` for Spanish):

```python
"""Spanish (es) locale — UI strings."""

from __future__ import annotations

LANG_CODE = "es"
LANG_NAME = "Español"
FLAG = "🇪🇸"

# Copy all strings from en.py or it.py and translate
MSG_START = (
    "👋 **¡Bienvenido a la Tienda de Tarjetas Coleccionables!**\n\n"
    "🃏 Navega por nuestras categorías...\n\n"
    "Elige una opción ⬇️"
)

MSG_CATEGORIES_MENU = "📂 **Categorías**\n\nElige una categoría:"

# ... all other strings ...
```

#### 2. Verify Auto-Detection

The system automatically detects new locale files! No code changes needed.

```python
# app/bot/i18n/__init__.py already handles auto-discovery
def get_available_languages() -> dict[str, str]:
    """Auto-detect languages from files in i18n/"""
    # ... auto-discovery magic ✨
```

#### 3. Test the New Language

```bash
python app/main.py
```

The new language will appear in the **🌍 Language** menu.

---

## 🧪 Testing

### Linting and Formatting

```bash
# Check style errors
ruff check app/

# Auto-fix errors
ruff check --fix app/

# Code formatting
ruff format app/

# Check formatting (without modifying)
ruff format --check app/
```

### Functional Testing

#### Complete Manual Test

1. **Basic User Test:**
   - [ ] `/start` shows menu with image
   - [ ] Language switch works
   - [ ] Category navigation works
   - [ ] Card view with video
   - [ ] Video deletes after 60s
   - [ ] Leave review (1st time)
   - [ ] Attempt duplicate review (should block)
   - [ ] Leave 4 reviews in 1h (4th should block)

2. **Admin Test:**
   - [ ] Access `/admin`
   - [ ] Add card (complete FSM workflow)
   - [ ] Update existing card video
   - [ ] Delete card (double confirmation)
   - [ ] Verify backup created in `data/backups/`
   - [ ] View category with 10+ cards (pagination)

3. **Security Test:**
   - [ ] Try YAML special characters in title (e.g., `:test`)
   - [ ] Try uploading .exe file as video (should block)
   - [ ] Try comment with 300+ characters (should truncate to 200)

#### Unit Test (Example)

```python
# tests/test_security.py
import pytest
from app.bot.database import sanitize_text, validate_video_mimetype

def test_sanitize_yaml_injection():
    """Test YAML injection prevention"""
    result = sanitize_text(":dangerous")
    assert not result.startswith(":"), "YAML special char not escaped"

def test_video_format_validation():
    """Test video format validation"""
    assert validate_video_mimetype("video.mp4") == True
    assert validate_video_mimetype("malware.exe") == False

def test_input_length_limit():
    """Test input length limit"""
    result = sanitize_text("A" * 100, max_length=50)
    assert len(result) == 50
```

Run tests:

```bash
pytest tests/ -v
```

---

## 📚 API Reference

### Main Database Functions

#### `add_card()`

Adds a new card to the database.

```python
async def add_card(
    category: str,
    title: str,
    video_id: str,
    description: str,
    admin_id: int | None = None
) -> int:
    """
    Args:
        category: Category (yugioh, pokemon, magic, altro)
        title: Card title
        video_id: Telegram file_id of the video
        description: Description and price
        admin_id: Admin ID for audit log

    Returns:
        int: TinyDB document ID

    Raises:
        Exception: If save fails
    """
```

**Automatic actions:**

- Input sanitization (title, description)
- Database backup creation
- Audit log if admin_id provided

---

#### `get_cards()`

Retrieves all cards from a category.

```python
async def get_cards(category: str) -> list[tuple[int, str]]:
    """
    Args:
        category: Category to filter

    Returns:
        List of tuples (card_id, title)

    Example:
        >>> await get_cards("yugioh")
        [(1, "Blue-Eyes White Dragon"), (4, "Dark Magician")]
    """
```

---

#### `add_review()`

Adds a review to a card.

```python
async def add_review(
    card_id: int,
    user_id: int,
    rating: int,
    comment: str = ""
) -> None:
    """
    Args:
        card_id: Card ID to review
        user_id: Telegram user ID
        rating: Rating from 1 to 5
        comment: Optional comment

    Raises:
        ValueError: If user has already reviewed this card
    """
```

**Validations:**

- Checks for duplicate review
- Sanitizes comment (max 200 characters)
- Verifies rating 1-5

---

#### `user_has_reviewed()`

Checks if a user has already reviewed a card.

```python
async def user_has_reviewed(card_id: int, user_id: int) -> bool:
    """
    Args:
        card_id: Card ID
        user_id: Telegram user ID

    Returns:
        True if user has already reviewed
    """
```

---

#### `validate_video_mimetype()`

Validates a video file format.

```python
def validate_video_mimetype(file_name: str | None) -> bool:
    """
    Args:
        file_name: Filename with extension

    Returns:
        True if valid video format

    Accepted formats:
        .mp4, .mov, .avi, .mkv, .webm, .flv, .mpeg, .mpg
    """
```

---

### Audit Logging Functions

#### `log_card_add()`

```python
def log_card_add(user_id: int, card_id: int, title: str, category: str) -> None:
    """Record card creation"""
```

#### `log_card_delete()`

```python
def log_card_delete(user_id: int, card_id: int, title: str) -> None:
    """Record card deletion"""
```

#### `log_video_update()`

```python
def log_video_update(user_id: int, card_id: int, title: str) -> None:
    """Record video update"""
```

#### `log_security_event()`

```python
def log_security_event(event_type: str, user_id: int, details: str = "") -> None:
    """
    Record security event

    Args:
        event_type: Event type (e.g., "RATE_LIMIT", "DUPLICATE_REVIEW")
        user_id: Telegram user ID
        details: Additional details
    """
```

---

## ⚙️ Advanced Configuration

### Environment Variables (.env)

```env
# === REQUIRED ===

# Bot token from @BotFather
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567

# Admin ID list (comma-separated)
ADMIN_IDS=123456789,987654321

# === OPTIONAL ===

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

> 💡 **Tip:** Use `LOG_LEVEL=DEBUG` for detailed troubleshooting without modifying the code.

### Configurable Constants (config.py)

```python
# Length limits
MAX_TITLE_LENGTH = 100              # Card title
MAX_DESCRIPTION_LENGTH = 500        # Card description

# Timing
AUTO_DELETE_VIDEO_SECONDS = 60      # Auto-delete video
WARNING_MESSAGE_DURATION = 3        # Warning message duration
FSM_TIMEOUT_SECONDS = 300           # FSM session timeout (5 min)

# Rate limiting
RATE_LIMIT_WINDOW = 5               # Message rate limit window (seconds)
RATE_LIMIT_MAX_MESSAGES = 5         # Max messages per window
REVIEW_RATE_LIMIT_MAX = 3           # Max reviews per hour
REVIEW_RATE_LIMIT_WINDOW = 3600     # Review rate limit window (1 hour)

# UI
MAX_BUTTON_LENGTH = 30              # Maximum button text length
CARDS_PER_PAGE = 8                  # Cards per page

# Storage
MAX_VIDEO_SIZE_MB = 50              # Maximum video size
MAX_BACKUPS_KEPT = 5                # Number of backups to keep
```

---

## 🔧 Troubleshooting

### Common Errors

#### ❌ `ERROR: BOT_TOKEN missing from .env file`

**Cause:** `.env` file not configured or BOT_TOKEN empty

**Solution:**

```bash
# Verify .env exists
ls .env

# If it doesn't exist, create from template
cp .env.example .env

# Edit with your token
nano .env  # Linux/Mac
notepad .env  # Windows
```

---

#### ❌ `ERROR: ADMIN_IDS invalid. Use comma-separated integers.`

**Cause:** ADMIN_IDS is not in the correct format

**Solution:**

```env
# ❌ WRONG
ADMIN_IDS=abc123
ADMIN_IDS="123456789"

# ✅ CORRECT
ADMIN_IDS=123456789
ADMIN_IDS=123456789,987654321,555555555
```

---

#### ❌ Bot doesn't respond to commands

**Cause:** Bot not started or invalid token

**Diagnosis:**

```bash
# Verify bot is running
ps aux | grep python  # Linux
Get-Process python  # Windows

# Check logs
tail -f logs/bot.log
```

**Solution:**

1. Verify BOT_TOKEN is valid in `.env`
2. Restart bot: `python app/main.py`
3. Check firewall isn't blocking connections

---

#### ❌ `Failed to read YAML database`

**Cause:** `cards.yaml` file corrupted or invalid syntax

**Diagnosis:**

```python
import yaml
with open('data/cards.yaml', 'r', encoding='utf-8') as f:
    yaml.safe_load(f)  # Shows syntax error
```

**Solution:**

```bash
# Restore from backup
cp data/backups/cards_backup_*.yaml data/cards.yaml

# If no backup, recreate empty
echo "_default: {}" > data/cards.yaml
```

---

#### ❌ Docker container exits immediately

**Diagnosis:**

```bash
# Check logs
docker-compose logs bot

# Check health check
docker inspect telegram-bot | grep -A 10 Health
```

**Common solutions:**

- Verify `.env` is mounted correctly in `docker-compose.yml`
- Check file permissions (user `botuser` in the container)
- Verify dependencies installed: `docker-compose build --no-cache`

---

#### ❌ Rate limit always triggered

**Cause:** Timestamp registry not reset

**Solution:**

```bash
# Restart bot (resets memory registry)
docker-compose restart bot

# Or restart Python process
```

---

### Log Debugging

#### Increase Logging Verbosity

Set the `LOG_LEVEL` environment variable to `DEBUG`:

```bash
# Linux/Mac
export LOG_LEVEL=DEBUG
python app/main.py

# Windows PowerShell
$env:LOG_LEVEL = "DEBUG"
python app/main.py

# Docker
docker-compose exec bot sh -c "LOG_LEVEL=DEBUG python app/main.py"
```

Or in VS Code, use the **"Bot Telegram: Start (Debug Mode)"** configuration which automatically sets `LOG_LEVEL=DEBUG`.

#### Telegram-Specific Logs

```python
# Enable aiogram logging
import logging
logging.getLogger("aiogram").setLevel(logging.DEBUG)
```

---

## 🤝 Contributing

### Guidelines

1. **Fork** the repository
2. Create a **feature branch**: `git checkout -b feature/new-feature`
3. **Commit** your changes: `git commit -am 'Add new feature'`
4. **Push** to the branch: `git push origin feature/new-feature`
5. Open a **Pull Request**

### Standards

- ✅ Run `ruff check --fix app/` before committing
- ✅ Add type hints to all functions
- ✅ Document functions with docstrings
- ✅ Manually test your changes
- ✅ Update README if necessary

---

## 📄 License

This project is released for **educational** purposes.

---

## 🙏 Acknowledgments

- [Aiogram](https://docs.aiogram.dev/) - Telegram Bot Framework
- [TinyDB](https://tinydb.readthedocs.io/) - Embedded Python Database
- [Ruff](https://github.com/astral-sh/ruff) - Blazing-fast Python Linter
- [Docker](https://www.docker.com/) - Containerization Platform

---

## 📞 Support

For questions, issues, or suggestions:

- 📧 Email: [your-email@example.com]
- 💬 Telegram: [@your-username]
- 🐛 Issues: [GitHub Issues](repository-issues-url)

---

## 📈 Future Roadmap

- [ ] PostgreSQL database for production scale
- [ ] Push notification system for new cards
- [ ] Payment integration (Stripe/PayPal)
- [ ] Bot analytics dashboard
- [ ] Export review reports to PDF
- [ ] User wishlist system
- [ ] Admin-user support chat
- [ ] REST API for external integrations

---

## 📝 Changelog

### v1.2.0 — Hardened & Polished (February 17, 2026)

**Critical:**

- **Database thread safety** — `asyncio.Lock` on all write operations
- **Atomic YAML writes** — temp file + `os.replace()` prevents corruption
- **Improved sanitization** — regex for YAML characters + optional Markdown V2 escape

**Major:**

- **Removed legacy code** — deleted unused `app/handlers.py` and `app/keyboards.py`
- **User language persistence** — preferences saved to `data/user_languages.json`
- **Graceful shutdown** — clean cleanup on SIGTERM/SIGINT (cancel tasks, close DB)
- **Multilingual admin panel** — all admin messages localized (full i18n)
- **Locale import fallback** — language import errors handled with safe fallback

**Improvements:**

- **Fixed rate limit** — now blocks after N messages per window (was always allowing)
- **Safe callback decorator** — errors in callback handlers caught and logged
- **Task tracking** — video deletion task monitoring with cleanup
- **Advanced Docker healthcheck** — checks log file activity timestamp
- **`.env.example`** — configuration template added
- **Configurable log level** — `LOG_LEVEL` environment variable
- **Increased audit retention** — 50 MB / 20 backups (was 10 MB / 5)
- **Safe backup rotation** — errors handled per file
- **Type hints** extended to all main functions

### v1.1.0 — Security Hardened (February 15, 2026)

- Input sanitization (YAML injection, null bytes)
- Duplicate review prevention
- Video format validation
- Review rate limiting
- Admin action audit logging
- Card list pagination
- Basic i18n system (IT/EN)

---

**Version:** 1.2.0 (Hardened & Polished)  
**Last Updated:** February 17, 2026  
**Status:** ✅ Production Ready

Made with ❤️ and ☕
