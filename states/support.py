from aiogram.fsm.state import StatesGroup, State


class SupportState(StatesGroup):
    waiting_message = State()
    waiting_media = State()
    waiting_admin_response = State()