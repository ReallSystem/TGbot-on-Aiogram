import asyncio
import logging

from bot.bot import create_bot
from bot.dispatcher import create_dispatcher


async def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # bot instance
    bot = create_bot()

    # dispatcher
    dp = create_dispatcher()

    try:
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Bot втомився")