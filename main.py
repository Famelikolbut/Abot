import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.config import settings
from bot.handlers import router


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher()

    from database.database import AsyncSessionLocal
    from sqlalchemy import text
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT count(*) FROM videos"))
            count = result.scalar()
            logging.info(f"STARTUP DB CHECK: Found {count} videos in database.")
    except Exception as e:
        logging.error(f"STARTUP DB CHECK FAILED: {e}")

    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
