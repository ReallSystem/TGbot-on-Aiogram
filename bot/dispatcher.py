from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.admin import router as admin_router
from handlers.user import router as user_router


def create_dispatcher() -> Dispatcher:

    dp = Dispatcher(
        storage=MemoryStorage()
    )

    dp.include_router(user_router)
    dp.include_router(admin_router)

    return dp