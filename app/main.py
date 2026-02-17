"""
Bot entrypoint — Application startup and shutdown.

Run with: python -m app.main
or use the VS Code debugger with F5.
"""

import sys
from pathlib import Path

# Add project root to sys.path so 'app' module imports work when running this file directly
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

import asyncio
import contextlib
import logging
import signal

from aiogram import Bot, Dispatcher

from app.bot.config import ADMIN_IDS, BOT_TOKEN, CATEGORY_NAMES, DB_PATH
from app.bot.database import db
from app.bot.handlers import router
from app.bot.handlers.helpers import cancel_pending_deletions
from app.bot.i18n import initialize_locales
from app.bot.logger import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    """Start the bot in long-polling mode."""
    # Initialize i18n system
    initialize_locales()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Bot started")
    logger.info("Active admins: %d", len(ADMIN_IDS))
    logger.info("Categories: %s", ", ".join(CATEGORY_NAMES))
    logger.info("Database: %s", DB_PATH)

    # Register graceful shutdown on SIGTERM (Docker / systemd)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):
            # Windows does not support add_signal_handler; KeyboardInterrupt path is fine
            loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown(dp)))

    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down gracefully...")
        cancel_pending_deletions()
        db.close()
        await bot.session.close()
        logger.info("Bot stopped")


async def _shutdown(dp: Dispatcher) -> None:
    """Signal handler helper — stop the dispatcher."""
    logger.info("Received shutdown signal")
    await dp.stop_polling()


if __name__ == "__main__":
    setup_logging()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually")
