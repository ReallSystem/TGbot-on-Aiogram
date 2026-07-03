import asyncio
import logging

from bot.bot import create_bot
from bot.dispatcher import create_dispatcher
from db import init_db


async def main():
    # Configure bot logging for application diagnostics.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    # Ініціалізувати БД
    init_db()
    logging.info("Database initialized")

    # Create the bot instance and dispatcher for polling.
    bot = create_bot()
    dp = create_dispatcher()

    try:
        await dp.start_polling(bot)

    finally:
        # Always close the bot HTTP session when polling stops.
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Bot втомився")