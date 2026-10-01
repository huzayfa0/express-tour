import re
import logging
from datetime import datetime
from aiogram import Router, F, Bot

logger = logging.getLogger(__name__)
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from bot.states import VisaStates
from bot.keyboards import (
    get_visa_countries_keyboard,
    get_visa_purposes_keyboard,
    get_timeframes_keyboard,
    get_visa_refusal_keyboard,
    get_refusal_count_keyboard,
    get_phone_keyboard,
    get_cancel_keyboard,
    get_convenient_time_keyboard,
    get_main_inline_keyboard,
    get_main_reply_keyboard,
    get_admin_lead_keyboard
)
from database import crud
from config import config

router = Router()

def clean_phone_number(raw_phone: str) -> str:
    cleaned = re.sub(r"[^\d+]", "", raw_phone)
    if cleaned.startswith("998") and not cleaned.startswith("+"):
        cleaned = "+" + cleaned
    elif len(cleaned) == 9 and not cleaned.startswith("+"):
        cleaned = "+998" + cleaned
    return cleaned

def is_valid_phone(phone: str) -> bool:
    cleaned = clean_phone_number(phone)
    return bool(re.match(r"^\+?\d{9,15}$", cleaned))


# 1-qadam: Viza olishni boshlash
@router.message(Command("visa"))
@router.message(F.text == "🛂 Viza olish")
@router.callback_query(F.data == "menu_visa")
async def start_visa_flow(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(VisaStates.country)
    text = (
        "🛂 <b>Viza olish bo'limi</b>\n\n"
        "1-qadam: Qaysi davlatga viza olmoqchisiz?\n"
        "Quyidagi davlatlardan birini tanlang:"
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_visa_countries_keyboard())
        await event.answer()
    else:
        await event.answer(text=text, parse_mode="HTML", reply_markup=get_visa_countries_keyboard())


# Davlat tanlanganda
@router.callback_query(VisaStates.country, F.data.startswith("visa_c_"))
async def process_visa_country(callback: CallbackQuery, state: FSMContext):
    country = callback.data.replace("visa_c_", "")
    if country == "boshqa":
        await state.set_state(VisaStates.custom_country)
        await callback.message.edit_text(
            "🌍 Iltimos, bormoqchi bo'lgan davlatingiz nomini yozing:",
            reply_markup=get_cancel_keyboard()
        )
    else:
        await state.update_data(country=country)
        await state.set_state(VisaStates.purpose)
        await callback.message.edit_text(
            f"Tanlandi: <b>{country}</b>\n\n2-qadam: Safaringiz maqsadi nima?",
            parse_mode="HTML",
            reply_markup=get_visa_purposes_keyboard()
        )
    await callback.answer()


@router.message(VisaStates.custom_country, F.text)
async def process_custom_country(message: Message, state: FSMContext):
    country = message.text.strip()
    await state.update_data(country=country)
    await state.set_state(VisaStates.purpose)
    await message.answer(
        f"Tanlandi: <b>{country}</b>\n\n2-qadam: Safaringiz maqsadi nima?",
        parse_mode="HTML",
        reply_markup=get_visa_purposes_keyboard()
    )


# 2-qadam: Maqsad tanlanganda
@router.callback_query(VisaStates.purpose, F.data.startswith("visa_p_"))
async def process_visa_purpose(callback: CallbackQuery, state: FSMContext):
    purpose = callback.data.replace("visa_p_", "")
    await state.update_data(purpose=purpose)
    await state.set_state(VisaStates.timeframe)
    await callback.message.edit_text(
        f"Maqsad: <b>{purpose}</b>\n\n3-qadam: Qachon ketishni rejalashtiryapsiz?",
        parse_mode="HTML",
        reply_markup=get_timeframes_keyboard()
    )
    await callback.answer()


# 3-qadam: Muddat tanlanganda
@router.callback_query(VisaStates.timeframe, F.data.startswith("time_"))
async def process_visa_timeframe(callback: CallbackQuery, state: FSMContext):
    timeframe = callback.data.replace("time_", "")
    await state.update_data(timeframe=timeframe)
    await state.set_state(VisaStates.refusal)
    await callback.message.edit_text(
        f"Muddat: <b>{timeframe}</b>\n\n4-qadam: Avval ushbu yoki boshqa davlatdan viza rad javobi (otkaz) bo'lganmi?",
        parse_mode="HTML",
        reply_markup=get_visa_refusal_keyboard()
    )
    await callback.answer()


# 4-qadam: Rad javobi
@router.callback_query(VisaStates.refusal, F.data == "refusal_yes")
async def process_refusal_yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(VisaStates.refusal_count)
    await callback.message.edit_text(
        "Necha marta rad javobi berilgan?",
        reply_markup=get_refusal_count_keyboard()
    )
    await callback.answer()


@router.callback_query(VisaStates.refusal, F.data == "refusal_no")
async def process_refusal_no(callback: CallbackQuery, state: FSMContext):
    await state.update_data(refusal_count=0)
    await state.set_state(VisaStates.name)
    await callback.message.edit_text(
        "5-qadam: Iltimos, to'liq ism-familiyangizni kiriting:\n(Masalan: Alisher Valiyev)"
    )
    await callback.answer()


@router.callback_query(VisaStates.refusal_count, F.data.startswith("refcnt_"))
async def process_refusal_count(callback: CallbackQuery, state: FSMContext):
    cnt_str = callback.data.replace("refcnt_", "")
    count = 3 if cnt_str == "3+" else int(cnt_str)
    await state.update_data(refusal_count=count)
    await state.set_state(VisaStates.name)
    await callback.message.edit_text(
        "5-qadam: Iltimos, to'liq ism-familiyangizni kiriting:\n(Masalan: Alisher Valiyev)"
    )
    await callback.answer()


# 5-qadam: Ism
@router.message(VisaStates.name, F.text)
async def process_visa_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or any(char.isdigit() for char in name):
        await message.answer("⚠️ Iltimos, haqiqiy ism-familiyangizni kiriting (raqamsiz):")
        return

    await state.update_data(name=name)
    await state.set_state(VisaStates.phone)
    await message.answer(
        f"Rahmat, <b>{name}</b>!\n\n"
        "6-qadam: Siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring.\n"
        "Iltimos, pastdagi <b>«📱 Raqamimni yuborish»</b> tugmasini bosing:",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )


# 6-qadam: Telefon (Faqat kontakt ulashish orqali)
@router.message(VisaStates.phone, F.contact)
async def process_visa_phone_contact(message: Message, state: FSMContext):
    phone = clean_phone_number(message.contact.phone_number)
    await state.update_data(phone=phone)
    await state.set_state(VisaStates.convenient_time)
    await message.answer(
        "7-qadam: Konsultatsiya uchun qaysi vaqt oraliqida qo'ng'iroq qilishimiz qulay?",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "Vaqt oralig'ini tanlang 👇",
        reply_markup=get_convenient_time_keyboard()
    )


@router.message(VisaStates.phone, F.text)
async def process_visa_phone_text(message: Message, state: FSMContext):
    await message.answer(
        "⚠️ <b>Telefon raqamini qo'lda kiritish mumkin emas!</b>\n\n"
        "Haqiqiy raqamingizni tasdiqlash uchun, iltimos, pastdagi <b>«📱 Raqamimni yuborish»</b> tugmasini bosing 👇",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )


# 7-qadam: Qulay vaqt va Yakun
@router.callback_query(VisaStates.convenient_time, F.data.startswith("ctime_"))
async def process_visa_convenient_time(callback: CallbackQuery, state: FSMContext, bot: Bot, user_source: str = "direct"):
    ctime = callback.data.replace("ctime_", "")
    data = await state.get_data()
    await state.clear()

    country = data.get("country", "Noma'lum")
    purpose = data.get("purpose", "Turizm")
    timeframe = data.get("timeframe", "1-3 oy ichida")
    refusal_count = data.get("refusal_count", 0)
    name = data.get("name", "Noma'lum")
    phone = data.get("phone", "")

    # Save to DB
    lead = await crud.create_lead(
        user_id=callback.from_user.id,
        service="visa",
        country=country,
        purpose=purpose,
        timeframe=timeframe,
        refusal_count=refusal_count,
        name=name,
        phone=phone,
        convenient_time=ctime,
        source=user_source
    )

    # Confirmation to user
    confirmation_text = (
        f"✅ <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"📌 <b>Ariza raqami:</b> <code>#{lead.lead_number}</code>\n"
        f"🛂 <b>Yo'nalish:</b> {country} vizasi\n"
        f"👤 <b>Ism:</b> {name}\n"
        f"⏰ <b>Qulay vaqt:</b> {ctime}\n\n"
        f"Mutaxassisimiz belgilangan vaqt ichida siz bilan bog'lanadi.\n\n"
        f"📋 Ariza holatini kuzatish uchun bosh menyudagi <b>«📋 Arizam holati»</b> tugmasidan foydalanishingiz mumkin."
    )
    await callback.message.edit_text(
        confirmation_text,
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard()
    )
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_reply_keyboard()
    )
    await callback.answer("Ariza qabul qilindi!")

    # Admin group notification
    if config.ADMIN_GROUP_ID:
        refusal_text = f"Ha, {refusal_count} marta" if refusal_count > 0 else "Yo'q, birinchi marta"
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        admin_text = (
            f"🔥 <b>YANGI LID #{lead.lead_number}</b>\n"
            f"👤 <b>Ism:</b> {name}\n"
            f"📱 <b>Tel:</b> <code>{phone}</code>\n"
            f"🌍 <b>Davlat:</b> {country}\n"
            f"✈️ <b>Maqsad:</b> {purpose}\n"
            f"📅 <b>Muddat:</b> {timeframe}\n"
            f"❌ <b>Rad javobi:</b> {refusal_text}\n"
            f"⏰ <b>Qulay vaqt:</b> {ctime}\n"
            f"📊 <b>Manba:</b> <code>{user_source}</code>\n"
            f"🕐 <b>Vaqt:</b> {now_str}\n\n"
            f"👇 <b>Holatni belgilang:</b>"
        )
        try:
            await bot.send_message(
                chat_id=config.ADMIN_GROUP_ID,
                text=admin_text,
                parse_mode="HTML",
                reply_markup=get_admin_lead_keyboard(lead.id)
            )
        except Exception as e:
            logger.error(f"Error sending visa lead to admin group {config.ADMIN_GROUP_ID}: {e}")
