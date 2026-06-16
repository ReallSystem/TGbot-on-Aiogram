from aiogram import Bot
from config import TOKEN


def create_bot() -> Bot:
    return Bot(token=TOKEN)