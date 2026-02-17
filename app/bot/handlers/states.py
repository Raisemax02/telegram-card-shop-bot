"""FSM state groups — Finite State Machine definitions."""

from aiogram.fsm.state import State, StatesGroup


class UploadCard(StatesGroup):
    """Admin workflow: Category -> Title -> Video -> Description -> Save."""

    write_title = State()
    send_video = State()
    write_description = State()


class LeaveReview(StatesGroup):
    """User workflow: Rating -> Comment -> Save."""

    choose_rating = State()
    write_comment = State()


class UpdateCardVideo(StatesGroup):
    """Admin workflow: Update video for existing card."""

    send_video = State()


class UpdateCardTitle(StatesGroup):
    """Admin workflow: Update title for existing card."""

    write_title = State()


class UpdateCardDescription(StatesGroup):
    """Admin workflow: Update description for existing card."""

    write_description = State()
