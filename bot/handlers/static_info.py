from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards import get_back_to_menu_keyboard
from database import crud
from config import config

router = Router()

# --- MANZIL VA ALOQA ---
@router.message(Command("contact"))
@router.message(F.text == "📍 Manzil va aloqa")
@router.callback_query(F.data == "menu_contact")
async def show_contact_info(event: Message | CallbackQuery):
    text = (
        f"📍 <b>«{config.COMPANY_NAME}» aloqa ma'lumotlari:</b>\n\n"
        f"🏢 <b>Manzil:</b> {config.COMPANY_ADDRESS}\n"
        f"🕒 <b>Ish vaqti:</b> {config.COMPANY_WORK_HOURS}\n"
        f"📞 <b>Telefon:</b> {config.COMPANY_PHONE}\n"
        f"✈️ <b>Telegram:</b> <a href=\"https://t.me/{config.COMPANY_TELEGRAM.lstrip('@')}\">{config.COMPANY_TELEGRAM}</a>\n"
        f"📸 <b>Instagram:</b> <a href=\"https://instagram.com/{config.COMPANY_INSTAGRAM.lstrip('@')}\">{config.COMPANY_INSTAGRAM}</a>\n\n"
        f"🗺️ <b>Google Xaritalar:</b> <a href=\"{config.GOOGLE_MAPS_URL}\">Xaritada ochish</a>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💬 Telegram: {config.COMPANY_TELEGRAM}", url=f"https://t.me/{config.COMPANY_TELEGRAM.lstrip('@')}")],
        [InlineKeyboardButton(text=f"📸 Instagram: {config.COMPANY_INSTAGRAM.lstrip('@')}", url=f"https://instagram.com/{config.COMPANY_INSTAGRAM.lstrip('@')}")],
        [InlineKeyboardButton(text="🗺️ Google Maps'da ko'rish", url=config.GOOGLE_MAPS_URL)],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")]
    ])

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
        await event.answer()
        if config.COMPANY_LAT and config.COMPANY_LON:
            try:
                await event.message.answer_location(latitude=config.COMPANY_LAT, longitude=config.COMPANY_LON)
            except Exception:
                pass
    else:
        await event.answer(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
        if config.COMPANY_LAT and config.COMPANY_LON:
            try:
                await event.answer_location(latitude=config.COMPANY_LAT, longitude=config.COMPANY_LON)
            except Exception:
                pass


# --- NATIJALARIMIZ ---
@router.message(Command("results"))
@router.message(F.text == "⭐ Natijalarimiz")
@router.callback_query(F.data == "menu_results")
async def show_results(event: Message | CallbackQuery):
    insta_url = f"https://instagram.com/{config.COMPANY_INSTAGRAM.lstrip('@')}"
    text = (
        f"⭐ <b>«{config.COMPANY_NAME}» muvaffaqiyatli natijalari:</b>\n\n"
        "Mijozlarimizning qo'lga kiritgan vizalari, nufuzli universitetlarga qabul xatlari, unutilmas sayohatlari va jonli video taassurotlari bilan rasmiy <b>Instagram</b> sahifamizda batafsil tanishishingiz mumkin!\n\n"
        f"📸 <b>Instagram:</b> <a href=\"{insta_url}\">{config.COMPANY_INSTAGRAM}</a>\n\n"
        "👇 Natijalarni ko'rish uchun quyidagi tugmani bosing:"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Instagram'da natijalarni ko'rish", url=insta_url)],
        [InlineKeyboardButton(text="💬 Men ham viza olmoqchiman", callback_data="menu_visa")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")]
    ])

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=False)
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=False)


# --- ESKI FAQ SO'ROVLARI (Olib tashlangan) ---
@router.callback_query(F.data == "menu_faq")
@router.callback_query(F.data.startswith("faq_c_"))
async def handle_removed_faq(callback: CallbackQuery):
    await callback.answer("Ushbu bo'lim olib tashlangan.", show_alert=True)

