import logging
from datetime import datetime
from aiogram import Router, F, Bot

logger = logging.getLogger(__name__)
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from bot.states import ConsultationStates
from bot.keyboards import (
    get_consult_service_keyboard,
    get_phone_keyboard,
    get_cancel_keyboard,
    get_convenient_time_keyboard,
    get_main_inline_keyboard,
    get_main_reply_keyboard,
    get_admin_lead_keyboard
)
from bot.handlers.visa import clean_phone_number, is_valid_phone
from database import crud
from config import config

router = Router()

# 1. Boshlash
@router.message(Command("consult"))
@router.message(F.text == "💬 Bepul konsultatsiya")
@router.callback_query(F.data == "menu_consult")
async def start_consult_flow(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ConsultationStates.service)
    text = (
        "💬 <b>Bepul mutaxassis konsultatsiyasi</b>\n\n"
        "Qaysi yo'nalish bo'yicha savollaringiz bor?\n"
        "Yo'nalishni tanlang:"
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_consult_service_keyboard())
        await event.answer()
    else:
        await event.answer(text=text, parse_mode="HTML", reply_markup=get_consult_service_keyboard())


# 2. Xizmat tanlanganda
@router.callback_query(ConsultationStates.service, F.data.startswith("csrv_"))
async def process_consult_service(callback: CallbackQuery, state: FSMContext):
    service = callback.data.replace("csrv_", "")
    await state.update_data(service=service)
    await state.set_state(ConsultationStates.name)
    await callback.message.edit_text(
        f"Yo'nalish: <b>{service}</b>\n\n"
        "Iltimos, to'liq ism-familiyangizni kiriting:\n(Masalan: Jamshid Aliyev)",
        parse_mode="HTML"
    )
    await callback.answer()


# 3. Ism
@router.message(ConsultationStates.name, F.text)
async def process_consult_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or any(char.isdigit() for char in name):
        await message.answer("⚠️ Iltimos, haqiqiy ism-familiyangizni kiriting:")
        return

    await state.update_data(name=name)
    await state.set_state(ConsultationStates.phone)
    await message.answer(
        f"Rahmat, <b>{name}</b>!\n\n"
        "Siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring.\n"
        "Iltimos, pastdagi <b>«📱 Raqamimni yuborish»</b> tugmasini bosing:",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )


# 4. Telefon (Faqat kontakt ulashish orqali)
@router.message(ConsultationStates.phone, F.contact)
async def process_consult_phone_contact(message: Message, state: FSMContext):
    phone = clean_phone_number(message.contact.phone_number)
    await state.update_data(phone=phone)
    await state.set_state(ConsultationStates.convenient_time)
    await message.answer("Konsultatsiya uchun qaysi vaqt oralig'i qulay?", reply_markup=ReplyKeyboardRemove())
    await message.answer("Vaqt oralig'ini tanlang 👇", reply_markup=get_convenient_time_keyboard())


@router.message(ConsultationStates.phone, F.text)
async def process_consult_phone_text(message: Message, state: FSMContext):
    await message.answer(
        "⚠️ <b>Telefon raqamini qo'lda kiritish mumkin emas!</b>\n\n"
        "Haqiqiy raqamingizni tasdiqlash uchun, iltimos, pastdagi <b>«📱 Raqamimni yuborish»</b> tugmasini bosing 👇",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )


# 5. Qulay vaqt va Yakun
@router.callback_query(ConsultationStates.convenient_time, F.data.startswith("ctime_"))
async def process_consult_time(callback: CallbackQuery, state: FSMContext, bot: Bot, user_source: str = "direct"):
    ctime = callback.data.replace("ctime_", "")
    data = await state.get_data()
    await state.clear()

    srv = data.get("service", "Umumiy")
    name = data.get("name", "Noma'lum")
    phone = data.get("phone", "")

    lead = await crud.create_lead(
        user_id=callback.from_user.id,
        service="consult",
        purpose=srv,
        name=name,
        phone=phone,
        convenient_time=ctime,
        source=user_source,
        notes="Bepul konsultatsiya so'rovi (HOT)"
    )

    confirmation = (
        f"✅ <b>Konsultatsiya so'rovingiz qabul qilindi!</b>\n\n"
        f"📌 <b>Ariza raqami:</b> <code>#{lead.lead_number}</code>\n"
        f"👤 <b>Ism:</b> {name}\n"
        f"⏰ <b>Qulay vaqt:</b> {ctime}\n\n"
        f"Katta mutaxassisimiz tez fursatda siz bilan bog'lanadi va barcha savollaringizga to'liq javob beradi."
    )
    await callback.message.edit_text(confirmation, parse_mode="HTML", reply_markup=get_main_inline_keyboard())
    await callback.message.answer("Asosiy menyu:", reply_markup=get_main_reply_keyboard())
    await callback.answer("Qabul qilindi!")

    # Admin group notification with special HOT marker
    if config.ADMIN_GROUP_ID:
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        admin_text = (
            f"⭐ <b>QAYNOQ LID: BEPUL KONSULTATSIYA #{lead.lead_number}</b>\n"
            f"👤 <b>Ism:</b> {name}\n"
            f"📱 <b>Tel:</b> <code>{phone}</code>\n"
            f"🎯 <b>Yo'nalish:</b> {srv}\n"
            f"⏰ <b>Qulay vaqt:</b> {ctime}\n"
            f"📊 <b>Manba:</b> <code>{user_source}</code>\n"
            f"🕐 <b>Vaqt:</b> {now_str}\n\n"
            f"⚡ <i>Bu eng issiq lid, iltimos tezda bog'laning!</i>\n\n"
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
            logger.error(f"Error sending consultation lead to admin group {config.ADMIN_GROUP_ID}: {e}")
