"""
Bot handlers — Router configuration and sub-router registration.

Handlers are registered in priority order: language selection first,
then commands and FSM states, then callbacks, and finally the
anti-spam catch-all.
"""

from aiogram import Router

from .antispam import router as antispam_router
from .cards import router as cards_router
from .commands import router as commands_router
from .language import router as language_router
from .navigation import router as navigation_router
from .reviews import router as reviews_router

router = Router(name="main")

# Registration order matters: FSM handlers must be registered
# before the anti-spam catch-all that matches all messages.
router.include_router(language_router)
router.include_router(commands_router)
router.include_router(cards_router)
router.include_router(reviews_router)
router.include_router(navigation_router)
router.include_router(antispam_router)
