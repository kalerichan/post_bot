import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.channels import router as channels_router
from handlers.post_creation import router as post_router

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(start_router)
    dp.include_router(channels_router)
    dp.include_router(post_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())