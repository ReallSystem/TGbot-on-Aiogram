from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.user import router as user_router


def create_dispatcher() -> Dispatcher:

    dp = Dispatcher(
        storage=MemoryStorage()
    )

    dp.include_router(user_router)

    return dp