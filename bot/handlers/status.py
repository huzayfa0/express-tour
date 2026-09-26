from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import StatusCheckStates
from bot.keyboards import get_back_to_menu_keyboard, get_cancel_keyboard
from database import crud

router = Router()

STATUS_EMOJIS = {
    "YANGI": "🟡 Yangi qabul qilindi",
    "ALOQA": "📞 Aloqa o'rnatildi",
    "QUALIF": "✅ Hujjatlar tayyorlanmoqda",
    "KONSULT": "📅 Konsultatsiya o'tkazildi",
    "SHARTNOMA": "📝 Shartnoma imzolandi, hujjatlar tayyorlanmoqda",
    "ELCHIXONA": "🏛️ Hujjatlar elchixonaga topshirildi",
    "VIZA_OLDI": "🎉 Tabriklaymiz, viza olindi!",
    "YUTQAZILDI": "❌ Rad javobi berildi yoki bekor qilindi",
    "KEYINROQ": "🔄 Vaqti keyinroqqa qoldirildi"
}

def render_stages(lead_status: str, created_at_str: str, updated_at_str: str) -> str:
    # 5 standard pipeline stages
    s1 = f"✅ <b>Ariza qabul qilindi</b> — {created_at_str}"
    
    if lead_status in ["KONSULT", "SHARTNOMA", "ELCHIXONA", "VIZA_OLDI"]:
        s2 = "✅ <b>Konsultatsiya o'tkazildi</b>"
    elif lead_status in ["ALOQA", "QUALIF"]:
        s2 = "🔵 <b>Konsultatsiya rejalashtirilmoqda</b>"
    else:
        s2 = "⬜ <b>Konsultatsiya</b>"

    if lead_status in ["SHARTNOMA", "ELCHIXONA", "VIZA_OLDI"]:
        s3 = "✅ <b>Hujjatlar tayyorlandi va tasdiqlandi</b>"
    elif lead_status in ["QUALIF", "KONSULT"]:
        s3 = "🔵 <b>Hujjatlar yig'ilmoqda va tekshirilmoqda</b>"
    else:
        s3 = "⬜ <b>Hujjatlar jarayonda</b>"

    if lead_status in ["ELCHIXONA", "VIZA_OLDI"]:
        s4 = "✅ <b>Elchixonaga topshirildi</b>"
    elif lead_status == "SHARTNOMA":
        s4 = "🔵 <b>Elchixonaga navbat olinmoqda</b>"
    else:
        s4 = "⬜ <b>Elchixonaga topshirish</b>"

    if lead_status == "VIZA_OLDI":
        s5 = "🎉 <b>NATIJA: Viza muvaffaqiyatli berildi!</b>"
    elif lead_status == "YUTQAZILDI":
        s5 = "❌ <b>NATIJA: Rad javobi berildi</b>"
    elif lead_status == "ELCHIXONA":
        s5 = "⏳ <b>Natija kutilmoqda (Elchixonada ko'rilmoqda)</b>"
    else:
        s5 = "⬜ <b>Natija</b>"

    return f"{s1}\n{s2}\n{s3}\n{s4}\n{s5}"


@router.message(Command("status"))
@router.message(F.text == "📋 Arizam holati")
@router.callback_query(F.data == "menu_status")
async def start_status_check(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StatusCheckStates.lead_number)
    text = (
        "📋 <b>Ariza holatini tekshirish</b>\n\n"
        "Iltimos, arizangiz raqamini kiriting:\n"
        "(Masalan: <code>ET-1001</code> yoki shunchaki <code>1001</code>)"
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_cancel_keyboard())
        await event.answer()
    else:
        await event.answer(text=text, parse_mode="HTML", reply_markup=get_cancel_keyboard())


@router.message(StatusCheckStates.lead_number, F.text)
async def process_lead_number_check(message: Message, state: FSMContext):
    lead_num = message.text.strip()
    lead = await crud.get_lead_by_number(lead_num)

    if not lead:
        await message.answer(
            f"⚠️ <b>#{lead_num}</b> raqamli ariza topilmadi.\n\n"
            "Iltimos, raqamni to'g'ri kiritganingizni tekshiring (Masalan: <code>ET-1001</code>):",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.clear()
    created_at_str = lead.created_at.strftime("%d.%m.%Y")
    updated_at_str = lead.updated_at.strftime("%d.%m.%Y %H:%M")
    status_label = STATUS_EMOJIS.get(lead.status, lead.status)
    stages_text = render_stages(lead.status, created_at_str, updated_at_str)

    country_info = f" | {lead.country}" if lead.country else ""
    direction = lead.service.capitalize()

    response_text = (
        f"📌 <b>Ariza #{lead.lead_number}</b>\n"
        f"👤 <b>{lead.name or 'Hurmatli mijoz'}</b> {country_info} ({direction})\n\n"
        f"📊 <b>Joriy holat:</b> {status_label}\n\n"
        f"<b>Bosqichlar:</b>\n"
        f"{stages_text}\n\n"
        f"⏰ <b>So'nggi yangilanish:</b> {updated_at_str}"
    )

    await message.answer(response_text, parse_mode="HTML", reply_markup=get_back_to_menu_keyboard())
