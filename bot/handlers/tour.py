import logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states import TourStates
from bot.keyboards import (
    get_tour_destinations_keyboard,
    get_tours_list_keyboard,
    get_tour_detail_keyboard,
    get_tour_people_keyboard,
    get_cancel_inline_keyboard,
    get_phone_keyboard,
    get_cancel_keyboard,
    get_main_inline_keyboard,
    get_main_reply_keyboard,
    get_admin_lead_keyboard
)
from bot.handlers.visa import clean_phone_number
from database import crud
from config import config

logger = logging.getLogger(__name__)
router = Router()

# 1. Boshlash
@router.message(Command("tour"))
@router.message(F.text == "✈️ Tur paketlar")
@router.callback_query(F.data == "menu_tour")
async def start_tour_flow(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(TourStates.destination)
    text = (
        "✈️ <b>Ajoyib sayohat va qaynoq tur paketlar bo'limi</b>\n\n"
        "Express Tour bilan dunyoning eng go'zal go'shalariga unutilmas sayohat qiling!\n"
        "Barcha turlarimizga <b>aviachipta, mehmonxona, transfer, tibbiy sug'urta va viza ko'magi</b> kiradi.\n\n"
        "Qaysi yo'nalish bo'yicha sayohat qilmoqchisiz?\n"
        "👇 Quyidagi mashhur yo'nalishlardan birini tanlang:"
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=text, parse_mode="HTML", reply_markup=get_tour_destinations_keyboard())
        await event.answer()
    else:
        await event.answer(text=text, parse_mode="HTML", reply_markup=get_tour_destinations_keyboard())


# 2. Yo'nalish tanlanganda yoki barcha turlar so'ralganda
@router.callback_query(F.data == "tour_all")
@router.callback_query(F.data.startswith("tour_d_"))
async def process_tour_destination(callback: CallbackQuery, state: FSMContext):
    if callback.data == "tour_all":
        dest = None
        dest_title = "Barcha qaynoq turlar"
    else:
        dest = callback.data.replace("tour_d_", "")
        dest_title = f"{dest} turlari"

    await state.update_data(destination=dest or "Boshqa")

    # DB dan aktiv turlarni olish
    tours = await crud.get_active_tours(dest)

    if tours:
        await state.set_state(TourStates.tour_select)
        await callback.message.edit_text(
            f"🌍 <b>{dest_title}</b> bo'yicha mavjud qaynoq takliflar:\n\n"
            "Batafsil ma'lumot va narxlarni ko'rish uchun kerakli turni tanlang 👇",
            parse_mode="HTML",
            reply_markup=get_tours_list_keyboard(tours, destination=dest)
        )
    else:
        # Agar bu yo'nalish bo'yicha hozircha tayyor tur bo'lmasa
        await state.set_state(TourStates.people_count)
        await callback.message.edit_text(
            f"🌍 <b>{dest or 'Siz tanlagan'}</b> yo'nalishi bo'yicha guruhlar individual tarzda shakllantirilmoqda.\n\n"
            "Sizga eng mos va qulay narx variantlarini hisoblab beramiz.\n"
            "👥 <b>Necha kishi bo'lib sayohat qilmoqchisiz?</b>",
            parse_mode="HTML",
            reply_markup=get_tour_people_keyboard()
        )
    await callback.answer()


# 3. Individual tur so'rovi
@router.callback_query(F.data == "tour_custom")
@router.callback_query(F.data.startswith("tour_custom_"))
async def process_tour_custom(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("tour_custom_"):
        dest = callback.data.replace("tour_custom_", "")
        await state.update_data(destination=dest, tour_title=f"Individual tur: {dest}")
        await state.set_state(TourStates.people_count)
        await callback.message.edit_text(
            f"✈️ <b>{dest}</b> bo'yicha individual sayohat buyurtmasi.\n\n"
            "👥 <b>Necha kishi bo'lib sayohat qilmoqchisiz?</b>\n"
            "Quyidagilardan birini tanlang:",
            parse_mode="HTML",
            reply_markup=get_tour_people_keyboard()
        )
    else:
        await state.set_state(TourStates.custom_destination)
        await callback.message.edit_text(
            "🌍 <b>Qaysi davlat yoki shaharga sayohat qilmoqchisiz?</b>\n\n"
            "(Masalan: <i>Gruziya, Maldiv orollari, Bali, Malayziya, Ozarbayjon</i>):",
            parse_mode="HTML",
            reply_markup=get_cancel_inline_keyboard()
        )
    await callback.answer()


@router.message(TourStates.custom_destination, F.text)
async def process_custom_dest_text(message: Message, state: FSMContext):
    dest = message.text.strip()
    await state.update_data(destination=dest, tour_title=f"Individual tur: {dest}")
    await state.set_state(TourStates.people_count)
    await message.answer(
        f"Tanlandi: <b>{dest}</b>\n\n"
        "👥 <b>Necha kishi bo'lib sayohat qilmoqchisiz?</b>\n"
        "Quyidagilardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=get_tour_people_keyboard()
    )


# 4. Aniq turni ko'rish
@router.callback_query(F.data.startswith("tour_id_"))
async def process_tour_view(callback: CallbackQuery, state: FSMContext):
    tour_id = int(callback.data.replace("tour_id_", ""))
    async with crud.AsyncSessionLocal() as session:
        from database.models import Tour
        tour = await session.get(Tour, tour_id)

    if not tour:
        await callback.answer("Tur topilmadi yoki muddati tugagan.", show_alert=True)
        return

    await state.update_data(
        selected_tour_id=tour.id,
        tour_title=tour.title,
        destination=tour.destination,
        price=tour.price_usd
    )

    text = (
        f"✈️ <b>{tour.title}</b>\n\n"
        f"📍 <b>Yo'nalish:</b> {tour.destination}\n"
        f"💵 <b>Narxi:</b> ${tour.price_usd:,.0f} dan boshlab (1 kishi uchun)\n\n"
        f"📝 <b>Tavsif va dastur:</b>\n{tour.description}\n\n"
        f"🎁 <b>Narx ichiga kiradi:</b>\n{tour.whats_included}\n\n"
        f"🎫 <b>Mavjud bo'sh o'rinlar:</b> {tour.slots_left} ta"
    )
    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_tour_detail_keyboard(tour.id, destination=tour.destination)
    )
    await callback.answer()


# 5. Turni band qilish
@router.callback_query(F.data.startswith("book_tour_"))
async def process_book_tour(callback: CallbackQuery, state: FSMContext):
    tour_id = int(callback.data.replace("book_tour_", ""))
    async with crud.AsyncSessionLocal() as session:
        from database.models import Tour
        tour = await session.get(Tour, tour_id)
        if tour:
            await state.update_data(
                selected_tour_id=tour.id,
                tour_title=tour.title,
                destination=tour.destination,
                price=tour.price_usd
            )

    await state.set_state(TourStates.people_count)
    await callback.message.edit_text(
        "👥 <b>Necha kishi bo'lib sayohat qilmoqchisiz?</b>\n\n"
        "Quyidagi variantlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=get_tour_people_keyboard()
    )
    await callback.answer()


# 6. Odamlar soni tanlanganda
@router.callback_query(TourStates.people_count, F.data.startswith("tour_ppl_"))
async def process_tour_people(callback: CallbackQuery, state: FSMContext):
    ppl = callback.data.replace("tour_ppl_", "")
    await state.update_data(people_count=ppl)
    await state.set_state(TourStates.departure_date)
    await callback.message.edit_text(
        f"Tanlandi: <b>{ppl}</b>\n\n"
        "📅 <b>Qachon ketishni rejalashtiryapsiz?</b>\n"
        "Taxminiy sanani yoki oyni yozing:\n"
        "(Masalan: <i>15-oktyabr, Keyingi oy boshida, Yangi yilda</i>):",
        parse_mode="HTML",
        reply_markup=get_cancel_inline_keyboard()
    )
    await callback.answer()


# 7. Ketish sanasi
@router.message(TourStates.departure_date, F.text)
async def process_tour_date(message: Message, state: FSMContext):
    date_text = message.text.strip()
    await state.update_data(departure_date=date_text)
    await state.set_state(TourStates.name)
    await message.answer(
        "👤 <b>Iltimos, to'liq ism-familiyangizni kiriting:</b>\n"
        "(Masalan: <i>Jamshid Karimov</i>)",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


# 8. Ism
@router.message(TourStates.name, F.text)
async def process_tour_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or any(char.isdigit() for char in name):
        await message.answer(
            "⚠️ Iltimos, haqiqiy ism-familiyangizni to'g'ri kiriting:\n(Masalan: Jamshid Karimov)",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(name=name)
    await state.set_state(TourStates.phone)
    await message.answer(
        f"Rahmat, <b>{name}</b>!\n\n"
        "Siz bilan bog'lanishimiz va eng qulay reyslarni tanlab berishimiz uchun telefon raqamingizni yuboring.\n"
        "Iltimos, pastdagi <b>«📱 Raqamimni yuborish»</b> tugmasini bosing:",
        parse_mode="HTML",
        reply_markup=get_phone_keyboard()
    )


# 9. Telefon va Yakun (Faqat kontakt ulashish orqali)
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
    ppl = data.get("people_count", "1 kishi")
    dept_date = data.get("departure_date", "Yaqin orada")
    name = data.get("name", "Noma'lum")

    lead = await crud.create_lead(
        user_id=message.from_user.id,
        service="tour",
        country=dest,
        purpose=f"Tur: {tour_title}",
        timeframe=dept_date,
        name=name,
        phone=phone,
        convenient_time="Ixtiyoriy vaqt",
        source=user_source,
        notes=f"Tur: {tour_title} | Sayohatchilar: {ppl}"
    )

    confirmation = (
        f"✅ <b>Tur bo'yicha arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"📌 <b>Ariza raqami:</b> <code>#{lead.lead_number}</code>\n"
        f"✈️ <b>Tanlangan tur:</b> {tour_title}\n"
        f"👥 <b>Sayohatchilar soni:</b> {ppl}\n"
        f"📅 <b>Ketish vaqti:</b> {dept_date}\n"
        f"👤 <b>Ism:</b> {name}\n"
        f"📞 <b>Telefon:</b> {phone}\n\n"
        f"Mutaxassisimiz siz bilan tez orada bog'lanib, eng maqbul aviaqatnovlar va mehmonxona joylashuvlarini taqdim etadi."
    )
    await message.answer(confirmation, parse_mode="HTML", reply_markup=get_main_inline_keyboard())
    await message.answer("Asosiy menyu:", reply_markup=get_main_reply_keyboard())

    if config.ADMIN_GROUP_ID:
        now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        admin_text = (
            f"✈️ <b>YANGI TUR BUYURTMA #{lead.lead_number}</b>\n"
            f"👤 <b>Ism:</b> {name}\n"
            f"📱 <b>Tel:</b> <code>{phone}</code>\n"
            f"🌍 <b>Yo'nalish:</b> {dest}\n"
            f"🏝️ <b>Tur:</b> {tour_title}\n"
            f"👥 <b>Sayohatchilar:</b> {ppl}\n"
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
        except Exception as e:
            logger.error(f"Error sending tour lead to admin group {config.ADMIN_GROUP_ID}: {e}")

