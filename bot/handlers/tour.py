from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from bot.states import TourStates
from bot.keyboards import (
    get_tour_destinations_keyboard,
    get_tours_list_keyboard,
    get_tour_detail_keyboard,
    get_phone_keyboard,
    get_cancel_keyboard,
    get_main_inline_keyboard,
    get_main_reply_keyboard,
    get_admin_lead_keyboard
)
from bot.handlers.visa import clean_phone_number, is_valid_phone
from database import crud
from config import config

router = Router()

# 1. Boshlash
@router.message(Command("tour"))
@router.message(F.text == "✈️ Tur paketlar")
@router.callback_query(F.data == "menu_tour")
async def start_tour_flow(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(TourStates.destination)
    text = (
        "✈️ <b>Ajoyib sayohat va tur paketlar bo'limi</b>\n\n"
        "Qaysi yo'nalish bo'yicha sayohat qilmoqchisiz?\n"
        "Quyidagi mashhur yo'nalishlardan birini tanlang:"
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_tour_destinations_keyboard())
        await event.answer()
    else:
        await event.answer(text=text, parse_mode="HTML", reply_markup=get_tour_destinations_keyboard())


# 2. Yo'nalish tanlanganda
@router.callback_query(TourStates.destination, F.data.startswith("tour_d_"))
async def process_tour_destination(callback: CallbackQuery, state: FSMContext):
    dest = callback.data.replace("tour_d_", "")
    await state.update_data(destination=dest)

    # Fetch active tours from DB
    tours = await crud.get_active_tours(dest if dest != "Boshqa" else None)
    if tours:
        await state.set_state(TourStates.tour_select)
        await callback.message.edit_text(
            f"🌍 <b>{dest}</b> yo'nalishi bo'yicha mavjud qaynoq turlar:\n\n"
            "Batafsil ma'lumot olish uchun turni tanlang 👇",
            parse_mode="HTML",
            reply_markup=get_tours_list_keyboard(tours)
        )
    else:
        # If no specific tours in DB, let user submit a custom request
        await state.set_state(TourStates.departure_date)
        await callback.message.edit_text(
            f"🌍 <b>{dest}</b> yo'nalishi bo'yicha ayni damda individual guruhlar shakllantirilmoqda.\n\n"
            "Sizga eng yaxshi narxlarni taklif qilishimiz uchun taxminan qaysi sanalarda bormoqchisiz?\n"
            "(Masalan: Keyingi oy boshida, 15-oktyabr va h.k.):",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
    await callback.answer()


# 3. Aniq turni ko'rish
@router.callback_query(F.data.startswith("tour_id_"))
async def process_tour_view(callback: CallbackQuery, state: FSMContext):
    tour_id = int(callback.data.replace("tour_id_", ""))
    async with crud.AsyncSessionLocal() as session:
        from database.models import Tour
        tour = await session.get(Tour, tour_id)

    if not tour:
        await callback.answer("Tur topilmadi", show_alert=True)
        return

    await state.update_data(selected_tour_id=tour.id, tour_title=tour.title, destination=tour.destination)
    text = (
        f"✈️ <b>{tour.title}</b>\n\n"
        f"📍 <b>Yo'nalish:</b> {tour.destination}\n"
        f"💵 <b>Narxi:</b> ${tour.price_usd:,.0f} dan boshlab\n"
        f"📝 <b>Tavsif:</b>\n{tour.description}\n\n"
        f"✅ <b>Narx ichiga kiradi:</b>\n{tour.whats_included}\n\n"
        f"🎫 <b>Mavjud bo'sh o'rinlar:</b> {tour.slots_left} ta"
    )
    await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_tour_detail_keyboard(tour.id))
    await callback.answer()


# 4. Turni band qilish
@router.callback_query(F.data.startswith("book_tour_"))
async def process_book_tour(callback: CallbackQuery, state: FSMContext):
    tour_id = int(callback.data.replace("book_tour_", ""))
    await state.update_data(selected_tour_id=tour_id)
    await state.set_state(TourStates.departure_date)
    await callback.message.edit_text(
        "Qachon ketishni rejalashtiryapsiz? (Taxminiy sanani kiriting):",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


# 5. Ketish sanasi
@router.message(TourStates.departure_date, F.text)
async def process_tour_date(message: Message, state: FSMContext):
    date_text = message.text.strip()
    await state.update_data(departure_date=date_text)
    await state.set_state(TourStates.name)
    await message.answer(
        "Iltimos, to'liq ism-familiyangizni kiriting:\n(Masalan: Jamshid Karimov)",
        reply_markup=get_cancel_keyboard()
    )


# 6. Ism
@router.message(TourStates.name, F.text)
async def process_tour_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or any(char.isdigit() for char in name):
        await message.answer("⚠️ Iltimos, haqiqiy ism-familiyangizni kiriting:")
        return

    await state.update_data(name=name)
    await state.set_state(TourStates.phone)
    await message.answer(
        f"Rahmat, <b>{name}</b>!\n\n"
        "Siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring.\n"
        "Iltimos, pastdagi <b>«📱 Raqamimni yuborish»</b> tugmasini bosing:",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )


# 7. Telefon va Yakun (Faqat kontakt ulashish orqali)
@router.message(TourStates.phone, F.contact)
async def process_tour_phone_contact(message: Message, state: FSMContext, bot: Bot, user_source: str = "direct"):
    phone = clean_phone_number(message.contact.phone_number)
    await finish_tour_booking(message, state, phone, bot, user_source)


@router.message(TourStates.phone, F.text)
async def process_tour_phone_text(message: Message, state: FSMContext):
    await message.answer(
        "⚠️ <b>Telefon raqamini qo'lda kiritish mumkin emas!</b>\n\n"
        "Haqiqiy raqamingizni tasdiqlash uchun, iltimos, pastdagi <b>«📱 Raqamimni yuborish»</b> tugmasini bosing 👇",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )


async def finish_tour_booking(message: Message, state: FSMContext, phone: str, bot: Bot, user_source: str):
    data = await state.get_data()
    await state.clear()

    dest = data.get("destination", "Noma'lum")
    tour_title = data.get("tour_title", dest)
    dept_date = data.get("departure_date", "Yaqin orada")
    name = data.get("name", "Noma'lum")

    lead = await crud.create_lead(
        user_id=message.from_user.id,
        service="tour",
        country=dest,
        purpose="Sayohat / Dam olish",
        timeframe=dept_date,
        name=name,
        phone=phone,
        convenient_time="Ixtiyoriy vaqt",
        source=user_source,
        notes=f"Tur: {tour_title}"
    )

    confirmation = (
        f"✅ <b>Tur bo'yicha arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"📌 <b>Ariza raqami:</b> <code>#{lead.lead_number}</code>\n"
        f"✈️ <b>Tanlangan tur:</b> {tour_title}\n"
        f"📅 <b>Ketish vaqti:</b> {dept_date}\n"
        f"👤 <b>Ism:</b> {name}\n\n"
        f"Menejerimiz siz bilan tez orada bog'lanib, eng qulay reyslar va mehmonxona variantlarini taqdim etadi."
    )
    await message.answer(confirmation, parse_mode="HTML", reply_markup=get_main_inline_keyboard())
    await message.answer("Asosiy menyu:", reply_markup=get_main_reply_keyboard())

    if config.ADMIN_GROUP_ID:
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        admin_text = (
            f"✈️ <b>YANGI TUR ZAKAZ #{lead.lead_number}</b>\n"
            f"👤 <b>Ism:</b> {name}\n"
            f"📱 <b>Tel:</b> <code>{phone}</code>\n"
            f"🌍 <b>Yo'nalish:</b> {dest}\n"
            f"🏝️ <b>Tur:</b> {tour_title}\n"
            f"📅 <b>Ketish sanasi:</b> {dept_date}\n"
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
