from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📱 Raqamimni yuborish", request_contact=True)],
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🛂 Viza olish"), KeyboardButton(text="🎓 Xorijda o'qish")],
        [KeyboardButton(text="✈️ Tur paketlar"), KeyboardButton(text="💬 Bepul konsultatsiya")],
        [KeyboardButton(text="⭐ Natijalarimiz"), KeyboardButton(text="📋 Arizam holati")],
        [KeyboardButton(text="📍 Manzil va aloqa")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
