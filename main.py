import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import config
from database.base import init_db, engine
from bot.middlewares import UserTrackingMiddleware
from bot.handlers import main_router
from bot.utils import setup_scheduler, set_bot_commands

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ExpressTourBot")

async def main():
    logger.info("Initializing Express Tour Bot...")

    # 1. Initialize Database tables
    try:
        await init_db()
        from database.crud import seed_initial_tours
        await seed_initial_tours()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return

    # 2. Check Bot Token
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.warning(
            "\n" + "="*60 + "\n"
            "DIQQAT: Bot tokeni topilmadi yoki kiritilmagan!\n"
            "Iltimos, '.env' faylini ochib, BOT_TOKEN qatoriga BotFather bergan tokeningizni yozing.\n"
            "Misol: BOT_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxxxx\n"
            + "="*60
        )
        return

    # 3. Setup Storage (Redis or Memory)
    storage = None
    if config.REDIS_URL:
        try:
            from aiogram.fsm.storage.redis import RedisStorage
            storage = RedisStorage.from_url(config.REDIS_URL)
            logger.info("Using RedisStorage for FSM.")
        except Exception as e:
            logger.warning(f"Could not connect to Redis ({e}), falling back to MemoryStorage.")
            storage = MemoryStorage()
    else:
        storage = MemoryStorage()
        logger.info("Using MemoryStorage for FSM.")

    # 4. Initialize Bot & Dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    # 5. Register Middlewares
    user_middleware = UserTrackingMiddleware()
    dp.message.middleware(user_middleware)
    dp.callback_query.middleware(user_middleware)

    # 6. Include Handlers
    dp.include_router(main_router)

    # 7. Setup Background Scheduler for Reminders
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("Background reminder scheduler started.")

    # 8. Set Bot Commands Menu (skripka yonidagi tezkor komandalar)
    await set_bot_commands(bot)

    # 9. Start Polling
    try:
        logger.info("Bot is starting polling...")
        # Delete pending webhook updates if any
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Shutting down bot...")
        scheduler.shutdown()
        await engine.dispose()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
