import logging
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from config import config

logger = logging.getLogger(__name__)

async def set_bot_commands(bot: Bot):
    """
    Telegram interfeysida skripka (📎) yonidagi "Menu" tugmasi
    va tezkor buyruqlar ro'yxatini sozlaydi.
    """
    user_commands = [
        BotCommand(command="start", description="🔄 Bosh menyu"),
        BotCommand(command="help", description="ℹ️ Yordam va qo'llanma"),
        BotCommand(command="visa", description="🛂 Viza olish"),
        BotCommand(command="study", description="🎓 Xorijda o'qish"),
        BotCommand(command="tour", description="✈️ Tur paketlar"),
        BotCommand(command="consult", description="💬 Bepul konsultatsiya"),
        BotCommand(command="status", description="📋 Arizam holatini tekshirish"),
        BotCommand(command="contact", description="📍 Manzil va aloqa"),
        BotCommand(command="cancel", description="❌ Amalni bekor qilish"),
    ]

    try:
        await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())
        logger.info("Default user commands set successfully.")
    except Exception as e:
        logger.error(f"Failed to set default commands: {e}")

    # Admin guruhi uchun maxsus admin buyruqlarini sozlash
    if config.ADMIN_GROUP_ID:
        admin_commands = [
            BotCommand(command="stats", description="📊 Bugungi statistika"),
            BotCommand(command="leads", description="📋 Oxirgi arizalar"),
            BotCommand(command="hot", description="🔥 Bog'lanilmagan lidlar"),
            BotCommand(command="tour_add", description="✈️ Yangi tur qo'shish"),
            BotCommand(command="faq_add", description="📚 FAQ qo'shish"),
            BotCommand(command="result_add", description="⭐ Natija qo'shish"),
            BotCommand(command="broadcast", description="📢 Hammaga xabar"),
        ]
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=config.ADMIN_GROUP_ID))
            logger.info("Admin group commands set successfully.")
        except Exception as e:
            logger.warning(f"Could not set admin group commands: {e}")
