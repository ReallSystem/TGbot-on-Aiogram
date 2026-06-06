from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters.command import Command, CommandStart
from handlers import user 

async def main():
    bot = Bot(token = 'SKYNET_TOKEN')
    dp = Dispatcher()
    dp.include_routers(user)
    await dp.start_polling(bot)
    

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Вербелик зупинився і це зробили ви') 

