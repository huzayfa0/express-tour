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
    results = await crud.get_results(limit=5)
    
    if results:
        text = "⭐ <b>Mijozlarimizning muvaffaqiyatli natijalari:</b>\n\n"
        for r in results:
            text += (
                f"🎉 <b>{r.full_name}</b> | <b>{r.country} ({r.service})</b>\n"
                f"💬 <i>\"{r.content}\"</i>\n"
                f"──────────────\n"
            )
    else:
        text = (
            "⭐ <b>Muvaffaqiyatli keyslarimiz va natijalar:</b>\n\n"
            "🎉 <b>Azizbek M.</b> — 🇬🇧 Buyuk Britaniya vizasi (Standard Visitor, 6 oy)\n"
            "💬 <i>\"Hujjatlarimni sifatli tayyorlab, 3 haftada viza olishimga yordam berishdi!\"</i>\n\n"
            "🎉 <b>Malika T.</b> — 🇺🇸 AQSh F-1 talaba vizasi (Webster University)\n"
            "💬 <i>\"Intervyuga zo'r tayyorlashdi, barcha savollarga aniq javob berib vizani oldim!\"</i>\n\n"
            "🎉 <b>Shohruh K.</b> — 🇪🇺 Shengen (Germaniya) vizasi\n"
            "💬 <i>\"Avval bir marta otkaz bo'lgan edi, Express Tour orqali qayta topshirib ijobiy javob oldim.\"</i>"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Men ham viza olmoqchiman", callback_data="menu_visa")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")]
    ])

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML", reply_markup=kb)


# --- FOYDALI MA'LUMOTLAR (FAQ) ---
@router.message(Command("faq"))
@router.message(F.text == "📚 Foydali ma'lumotlar")
@router.callback_query(F.data == "menu_faq")
async def show_faq_categories(event: Message | CallbackQuery):
    text = (
        "📚 <b>Foydali ma'lumotlar va ko'p beriladigan savollar:</b>\n\n"
        "Qaysi davlat bo'yicha ma'lumot olmoqchisiz?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇬🇧 Britaniya", callback_data="faq_c_Britaniya"),
            InlineKeyboardButton(text="🇺🇸 AQSh", callback_data="faq_c_AQSh")
        ],
        [
            InlineKeyboardButton(text="🇪🇺 Shengen", callback_data="faq_c_Shengen"),
            InlineKeyboardButton(text="🇨🇦 Kanada", callback_data="faq_c_Kanada")
        ],
        [
            InlineKeyboardButton(text="❓ Umumiy savol-javoblar", callback_data="faq_c_Umumiy")
        ],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")]
    ])

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("faq_c_"))
async def show_faq_content(callback: CallbackQuery):
    country = callback.data.replace("faq_c_", "")
    faqs = await crud.get_faqs(country=country)

    if faqs:
        text = f"📚 <b>{country} bo'yicha ma'lumotlar:</b>\n\n"
        for item in faqs:
            text += f"🔹 <b>{item.topic}:</b>\n{item.content}\n\n"
    else:
        # Default helpful guides
        if country == "Britaniya":
            text = (
                "🇬🇧 <b>Buyuk Britaniya vizasi bo'yicha ma'lumot:</b>\n\n"
                "📌 <b>Asosiy talab qilinadigan hujjatlar:</b>\n"
                "• Xorijga chiqish pasporti (kamida 6 oy amal qilish muddati bilan)\n"
                "• Ish joyidan ma'lumotnoma va daromad haqida tasdiqnoma\n"
                "• Bank hisob raqamidan ko'chirma (oxirgi 6 oy, yetarli mablag' bilan)\n"
                "• Mulk va ko'chmas mulk hujjatlari (mavjud bo'lsa)\n\n"
                "⏳ <b>Ko'rib chiqish muddati:</b> 15 ish kuni (tezlashtirilgan 5 kun)"
            )
        elif country == "AQSh":
            text = (
                "🇺🇸 <b>AQSh vizasi (B1/B2 va F1) bo'yicha ma'lumot:</b>\n\n"
                "📌 <b>Asosiy bosqichlar:</b>\n"
                "• DS-160 elektron anketasini xatosiz to'ldirish\n"
                "• Konsullik yig'imini to'lash va intervyuga navbat olish\n"
                "• Elchixonada konsul bilan suhbatdan muvaffaqiyatli o'tish\n\n"
                "💡 <i>Eng muhim omil: Vatan bilan bog'liqlik (ish, oila, mulk) va safar maqsadining aniqligi.</i>"
            )
        elif country == "Shengen":
            text = (
                "🇪🇺 <b>Shengen vizasi bo'yicha ma'lumot:</b>\n\n"
                "📌 <b>Asosiy talablar:</b>\n"
                "• Asosiy qolish davlati elchixonasiga topshirish qoidasi\n"
                "• Mehmonxona va aviachipta bronlari\n"
                "• Xalqaro tibbiy sug'urta (30 000 yevro qoplamali)\n"
                "• Moliyaviy ta'minlanganlik kafolati"
            )
        else:
            text = (
                f"🌍 <b>{country} vizasi bo'yicha ma'lumot:</b>\n\n"
                "Viza talablari sizning safar maqsadingiz, ish faoliyatingiz va moliyaviy holatingizga qarab individual belgilanadi.\n\n"
                "Aniq talablar va hujjatlar ro'yxatini bilish uchun mutaxassisimizdan bepul konsultatsiya oling."
            )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Bepul konsultatsiya olish", callback_data="menu_consult")],
        [InlineKeyboardButton(text="🔙 Boshqa davlatlar", callback_data="menu_faq")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")]
    ])
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()
