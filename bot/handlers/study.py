from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from bot.states import StudyStates
from bot.keyboards import (
    get_study_stages_keyboard,
    get_study_countries_keyboard,
    get_ielts_keyboard,
    get_study_budget_keyboard,
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

# 1-qadam: Boshlash
@router.message(Command("study"))
@router.message(F.text == "🎓 Xorijda o'qish")
@router.callback_query(F.data == "menu_study")
async def start_study_flow(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StudyStates.stage)
    text = (
        "🎓 <b>Xorijda nufuzli ta'lim olish bo'limi</b>\n\n"
        "1-qadam: Qaysi bosqichda ta'lim olmoqchisiz?\n"
        "Kerakli bosqichni tanlang:"
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_study_stages_keyboard())
        await event.answer()
    else:
        await event.answer(text=text, parse_mode="HTML", reply_markup=get_study_stages_keyboard())


# Bosqich tanlanganda
@router.callback_query(StudyStates.stage, F.data.startswith("study_st_"))
async def process_study_stage(callback: CallbackQuery, state: FSMContext):
    stage = callback.data.replace("study_st_", "")
    await state.update_data(stage=stage)
    await state.set_state(StudyStates.country)
    await callback.message.edit_text(
        f"Bosqich: <b>{stage}</b>\n\n2-qadam: Qaysi davlatda o'qishni rejalashtiryapsiz?",
        parse_mode="HTML",
        reply_markup=get_study_countries_keyboard()
    )
    await callback.answer()


# Davlat tanlanganda
@router.callback_query(StudyStates.country, F.data.startswith("study_c_"))
async def process_study_country(callback: CallbackQuery, state: FSMContext):
    country = callback.data.replace("study_c_", "")
    if country == "boshqa":
        await state.set_state(StudyStates.custom_country)
        await callback.message.edit_text(
            "🌍 Iltimos, o'qimoqchi bo'lgan davlatingiz nomini yozing:",
            reply_markup=get_cancel_keyboard()
        )
    else:
        await state.update_data(country=country)
        await state.set_state(StudyStates.ielts)
        await callback.message.edit_text(
            f"Davlat: <b>{country}</b>\n\n3-qadam: Sizda IELTS yoki til sertifikati bormi?",
            parse_mode="HTML",
            reply_markup=get_ielts_keyboard()
        )
    await callback.answer()


@router.message(StudyStates.custom_country, F.text)
async def process_study_custom_country(message: Message, state: FSMContext):
    country = message.text.strip()
    await state.update_data(country=country)
    await state.set_state(StudyStates.ielts)
    await message.answer(
        f"Davlat: <b>{country}</b>\n\n3-qadam: Sizda IELTS yoki til sertifikati bormi?",
        parse_mode="HTML",
        reply_markup=get_ielts_keyboard()
    )


# 3-qadam: IELTS
@router.callback_query(StudyStates.ielts, F.data == "ielts_yes")
async def process_ielts_yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StudyStates.ielts_score)
    await callback.message.edit_text(
        "Iltimos, IELTS balingizni kiriting:\n(Masalan: 6.5 yoki 7.0)",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(StudyStates.ielts_score, F.text)
async def process_ielts_score_text(message: Message, state: FSMContext):
    score = message.text.strip()
    await state.update_data(ielts_score=score)
    await state.set_state(StudyStates.budget)
    await message.answer(
        f"IELTS bali: <b>{score}</b>\n\n4-qadam: Yillik kontrakt va xarajatlar uchun byudjetingiz qancha?",
        parse_mode="HTML",
        reply_markup=get_study_budget_keyboard()
    )


@router.callback_query(StudyStates.ielts, F.data.in_(["ielts_no", "ielts_preparing"]))
async def process_ielts_other(callback: CallbackQuery, state: FSMContext):
    ans = "Tayyorlanmoqda" if callback.data == "ielts_preparing" else "Yo'q"
    await state.update_data(ielts_score=ans)
    await state.set_state(StudyStates.budget)
    
    note_extra = ""
    if ans == "Yo'q":
        note_extra = "\n<i>(Eslatma: Agar IELTS bo'lmasa, Express IELTS markazimiz orqali qisqa muddatda tayyorlanish imkoniyati mavjud)</i>\n"

    await callback.message.edit_text(
        f"IELTS: <b>{ans}</b>{note_extra}\n4-qadam: Yillik ta'lim va xarajatlar uchun byudjetingiz qancha?",
        parse_mode="HTML",
        reply_markup=get_study_budget_keyboard()
    )
    await callback.answer()


# 4-qadam: Byudjet
@router.callback_query(StudyStates.budget, F.data.startswith("budget_"))
async def process_study_budget(callback: CallbackQuery, state: FSMContext):
    budget = callback.data.replace("budget_", "")
    await state.update_data(budget=budget)
    await state.set_state(StudyStates.name)
    await callback.message.edit_text(
        f"Byudjet: <b>{budget}</b>\n\n"
        "5-qadam: Iltimos, to'liq ism-familiyangizni kiriting:\n(Masalan: Sardor Rustamov)"
    )
    await callback.answer()


# 5-qadam: Ism
@router.message(StudyStates.name, F.text)
async def process_study_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or any(char.isdigit() for char in name):
        await message.answer("⚠️ Iltimos, haqiqiy ism-familiyangizni kiriting (raqamsiz):")
        return

    await state.update_data(name=name)
    await state.set_state(StudyStates.phone)
    await message.answer(
        f"Rahmat, <b>{name}</b>!\n\n"
        "6-qadam: Siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring.\n"
        "«📱 Raqamimni yuborish» tugmasini bosing yoki <code>+998901234567</code> formatida yozing:",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )


# 6-qadam: Telefon
@router.message(StudyStates.phone, F.contact)
async def process_study_phone_contact(message: Message, state: FSMContext):
    phone = clean_phone_number(message.contact.phone_number)
    await state.update_data(phone=phone)
    await state.set_state(StudyStates.convenient_time)
    await message.answer(
        "7-qadam: Konsultatsiya uchun qaysi vaqt oraliqida qo'ng'iroq qilishimiz qulay?",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer("Vaqt oralig'ini tanlang 👇", reply_markup=get_convenient_time_keyboard())


@router.message(StudyStates.phone, F.text)
async def process_study_phone_text(message: Message, state: FSMContext):
    raw_phone = message.text.strip()
    if not is_valid_phone(raw_phone):
        await message.answer(
            "⚠️ Noto'g'ri telefon raqami kiritildi. Iltimos, <code>+998901234567</code> formatida yozing:",
            parse_mode="HTML"
        )
        return
    phone = clean_phone_number(raw_phone)
    await state.update_data(phone=phone)
    await state.set_state(StudyStates.convenient_time)
    await message.answer(
        "7-qadam: Konsultatsiya uchun qaysi vaqt oraliqida qo'ng'iroq qilishimiz qulay?",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer("Vaqt oralig'ini tanlang 👇", reply_markup=get_convenient_time_keyboard())


# 7-qadam: Qulay vaqt va Yakun
@router.callback_query(StudyStates.convenient_time, F.data.startswith("ctime_"))
async def process_study_convenient_time(callback: CallbackQuery, state: FSMContext, bot: Bot, user_source: str = "direct"):
    ctime = callback.data.replace("ctime_", "")
    data = await state.get_data()
    await state.clear()

    stage = data.get("stage", "Bakalavr")
    country = data.get("country", "Noma'lum")
    ielts = data.get("ielts_score", "Yo'q")
    budget = data.get("budget", "$3-7K")
    name = data.get("name", "Noma'lum")
    phone = data.get("phone", "")

    # Save to DB
    lead = await crud.create_lead(
        user_id=callback.from_user.id,
        service="study",
        stage=stage,
        country=country,
        ielts_score=ielts,
        budget=budget,
        name=name,
        phone=phone,
        convenient_time=ctime,
        source=user_source
    )

    confirmation_text = (
        f"✅ <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"📌 <b>Ariza raqami:</b> <code>#{lead.lead_number}</code>\n"
        f"🎓 <b>Yo'nalish:</b> {country} da ta'lim ({stage})\n"
        f"👤 <b>Ism:</b> {name}\n"
        f"⏰ <b>Qulay vaqt:</b> {ctime}\n\n"
        f"Ta'lim bo'yicha mutaxassisimiz tez orada siz bilan bog'lanib, universitetlar ro'yxati va grant imkoniyatlarini taqdim etadi."
    )
    await callback.message.edit_text(confirmation_text, parse_mode="HTML", reply_markup=get_main_inline_keyboard())
    await callback.message.answer("Asosiy menyu:", reply_markup=get_main_reply_keyboard())
    await callback.answer("Ariza qabul qilindi!")

    # Admin group notification
    if config.ADMIN_GROUP_ID:
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        admin_text = (
            f"🎓 <b>YANGI TA'LIM LIDI #{lead.lead_number}</b>\n"
            f"👤 <b>Ism:</b> {name}\n"
            f"📱 <b>Tel:</b> <code>{phone}</code>\n"
            f"🌍 <b>Davlat:</b> {country}\n"
            f"📚 <b>Bosqich:</b> {stage}\n"
            f"📝 <b>IELTS:</b> {ielts}\n"
            f"💰 <b>Byudjet:</b> {budget}\n"
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
        except Exception:
            pass
