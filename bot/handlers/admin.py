import asyncio
from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from bot.states import AdminStates
from bot.keyboards import get_admin_lead_keyboard, get_assign_manager_keyboard
from database import crud
from config import config, update_admin_group_id

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in config.SUPER_ADMIN_IDS


# --- ADMIN PANEL ASOSIY MENYU ---
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Sizda ushbu buyruqni bajarish huquqi yo'q.")
        return

    text = (
        "⚙️ <b>Express Tour | Admin Boshqaruv Paneli</b>\n\n"
        "Mavjud buyruqlar:\n"
        "📊 /stats — Bugungi to'liq statistika\n"
        "📋 /leads — Oxirgi 10 ta ariza\n"
        "🔥 /hot — Bog'lanilmagan issiq arizalar\n"
        "✈️ /tour_add — Yangi tur paket qo'shish\n"
        "📚 /faq_add — Yangi savol-javob qo'shish\n"
        "⭐ /result_add — Yangi muvaffaqiyatli natija qo'shish\n"
        "📢 /broadcast — Barcha foydalanuvchilarga xabar yuborish\n"
    )
    await message.answer(text, parse_mode="HTML")


# --- /stats STATISTIKA BUYRUG'I ---
@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not is_admin(message.from_user.id) and message.chat.id != config.ADMIN_GROUP_ID:
        await message.answer("⛔ Sizda statistika ko'rish huquqi yo'q.")
        return

    stats = await crud.get_today_stats()
    today_str = datetime.now().strftime("%d.%m.%Y")

    source_lines = ""
    for src, count in stats["sources"].items():
        source_lines += f"    {src}: {count}\n"
    if not source_lines:
        source_lines = "    Hozircha ma'lumot yo'q\n"

    report = (
        f"📊 <b>BUGUNGI STATISTIKA | {today_str}</b>\n\n"
        f"🔥 <b>Jami lidlar: {stats['total']} ta</b>\n"
        f"  ├ 🛂 Viza: {stats['visa']} ta\n"
        f"  ├ 🎓 O'qish: {stats['study']} ta\n"
        f"  ├ ✈️ Tur: {stats['tour']} ta\n"
        f"  └ 💬 Konsultatsiya: {stats['consult']} ta\n\n"
        f"📞 <b>Bog'lanildi:</b> {stats['contacted']} ta ({stats['contacted_percent']}%)\n"
        f"❌ <b>Bog'lanilmadi:</b> {stats['not_contacted']} ta\n"
        f"📅 <b>Konsultatsiya:</b> {stats['consultations']} ta\n"
        f"📝 <b>Shartnomalar:</b> {stats['contracts']} ta\n\n"
        f"📊 <b>Manbalar (UTM):</b>\n{source_lines}"
    )
    await message.answer(report, parse_mode="HTML")


# --- /leads OXIRGI LIDLAR ---
@router.message(Command("leads"))
async def cmd_leads(message: Message):
    if not is_admin(message.from_user.id) and message.chat.id != config.ADMIN_GROUP_ID:
        return

    leads = await crud.get_recent_leads(limit=10)
    if not leads:
        await message.answer("Hozircha arizalar mavjud emas.")
        return

    text = "📋 <b>Oxirgi 10 ta ariza:</b>\n\n"
    for l in leads:
        time_str = l.created_at.strftime("%d.%m %H:%M")
        text += (
            f"• <b>#{l.lead_number}</b> | {l.name or 'Noma\'lum'} | {l.phone or ''}\n"
            f"  {l.service.upper()} ({l.country or ''}) — <b>{l.status}</b> [{time_str}]\n\n"
        )
    await message.answer(text, parse_mode="HTML")


# --- /hot ISSIQ LIDLAR ---
@router.message(Command("hot"))
async def cmd_hot(message: Message):
    if not is_admin(message.from_user.id) and message.chat.id != config.ADMIN_GROUP_ID:
        return

    hot_leads = await crud.get_hot_leads(limit=10)
    if not hot_leads:
        await message.answer("🎉 Ajoyib! Hozircha barcha issiq lidlar bilan bog'lanilgan.")
        return

    text = "🔥 <b>Hali bog'lanilmagan issiq lidlar:</b>\n\n"
    for l in hot_leads:
        text += (
            f"⚡ <b>#{l.lead_number}</b> | {l.name or 'Noma\'lum'}\n"
            f"📱 Tel: <code>{l.phone}</code>\n"
            f"🌍 Yo'nalish: {l.service.capitalize()} | {l.country or ''}\n"
            f"⏰ Qulay vaqt: {l.convenient_time or 'Tezda'}\n\n"
        )
    await message.answer(text, parse_mode="HTML")


# --- STATUS O'ZGARTIRISH (INLINE TUGMALAR) ---
@router.callback_query(F.data.startswith("lead_st_"))
async def process_lead_status_change(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split("_")
    lead_id = int(parts[2])
    new_status = parts[3]
    mgr_id = callback.from_user.id
    mgr_name = callback.from_user.full_name

    lead = await crud.update_lead_status(
        lead_id=lead_id,
        new_status=new_status,
        changed_by=mgr_id,
        note=f"Status {mgr_name} tomonidan o'zgartirildi"
    )

    if not lead:
        await callback.answer("Ariza topilmadi", show_alert=True)
        return

    status_labels = {
        "ALOQA": "📞 Qo'ng'iroq qilindi",
        "QUALIF": "✅ Malakali (Qualif)",
        "BOGLANMADI": "❌ Bog'lanib bo'lmadi",
        "KONSULT": "📅 Konsultatsiya belgilandi",
        "SHARTNOMA": "📝 Shartnoma imzolandi",
        "ELCHIXONA": "🏛️ Elchixonaga topshirildi",
        "VIZA_OLDI": "🎉 Viza olindi",
        "YUTQAZILDI": "❌ Yutqazildi"
    }
    label = status_labels.get(new_status, new_status)
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Update admin message text with badge
    original_text = callback.message.html_text or callback.message.text
    badge = f"\n\n⚡ <b>Oxirgi status:</b> {label} ({mgr_name}, {now_str})"
    
    # Avoid duplicate badges
    if "Oxirgi status:" in original_text:
        base_text = original_text.split("Oxirgi status:")[0].strip()
        updated_text = base_text + badge
    else:
        updated_text = original_text + badge

    try:
        await callback.message.edit_text(
            text=updated_text,
            parse_mode="HTML",
            reply_markup=get_admin_lead_keyboard(lead_id)
        )
    except Exception:
        pass

    await callback.answer(f"Status: {label}")

    # Notify user in PM if significant stage
    if new_status in ["KONSULT", "SHARTNOMA", "ELCHIXONA", "VIZA_OLDI"]:
        user_msg = ""
        if new_status == "KONSULT":
            user_msg = f"📅 <b>Hurmatli {lead.name}!</b>\nSizning #{lead.lead_number} raqamli arizangiz bo'yicha mutaxassis konsultatsiyasi belgilandi."
        elif new_status == "SHARTNOMA":
            user_msg = f"📝 <b>Hurmatli {lead.name}!</b>\n#{lead.lead_number} raqamli arizangiz bo'yicha shartnoma bosqichiga o'tildi. Hujjatlaringiz tayyorlanmoqda."
        elif new_status == "ELCHIXONA":
            user_msg = f"🏛️ <b>Hurmatli {lead.name}!</b>\n#{lead.lead_number} raqamli viza hujjatingiz elchixonaga topshirildi! Natijani birgalikda kutamiz."
        elif new_status == "VIZA_OLDI":
            user_msg = f"🎉 <b>TABRIKLAYMIZ, {lead.name}!</b>\nSizning #{lead.lead_number} raqamli arizangiz bo'yicha vizangiz muvaffaqiyatli chiqdi!"

        if user_msg:
            try:
                await bot.send_message(chat_id=lead.user_id, text=user_msg, parse_mode="HTML")
            except Exception:
                pass


# --- MENYEJER TAYINLASH ---
@router.callback_query(F.data.startswith("lead_assign_"))
async def process_lead_assign_menu(callback: CallbackQuery):
    lead_id = int(callback.data.replace("lead_assign_", ""))
    managers = await crud.get_managers(active_only=True)
    if not managers:
        # Default self as manager
        await crud.add_or_update_manager(callback.from_user.id, callback.from_user.full_name, "super_admin")
        managers = await crud.get_managers(active_only=True)

    await callback.message.edit_reply_markup(
        reply_markup=get_assign_manager_keyboard(lead_id, managers)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lead_back_"))
async def process_lead_back_to_card(callback: CallbackQuery):
    lead_id = int(callback.data.replace("lead_back_", ""))
    await callback.message.edit_reply_markup(
        reply_markup=get_admin_lead_keyboard(lead_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_mgr_"))
async def process_set_manager(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split("_")
    lead_id = int(parts[2])
    mgr_id = int(parts[3])

    lead = await crud.assign_lead_manager(lead_id, mgr_id)
    if not lead:
        await callback.answer("Ariza topilmadi")
        return

    await callback.answer("Menejer biriktirildi!")
    await callback.message.edit_reply_markup(
        reply_markup=get_admin_lead_keyboard(lead_id)
    )

    # Notify assigned manager directly in PM
    try:
        await bot.send_message(
            chat_id=mgr_id,
            text=(
                f"👤 <b>Sizga yangi ariza biriktirildi!</b>\n\n"
                f"📌 Ariza: <b>#{lead.lead_number}</b>\n"
                f"👤 Mijoz: <b>{lead.name}</b>\n"
                f"📱 Telefon: <code>{lead.phone}</code>\n"
                f"🌍 Xizmat: {lead.service} ({lead.country or ''})\n"
                f"⏰ Qulay vaqt: {lead.convenient_time}\n\n"
                f"Iltimos, zudlik bilan aloqaga chiqing!"
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass


# --- KEYINROQ / ESLATMA QO'YISH ---
@router.callback_query(F.data.startswith("lead_remind_"))
async def process_remind_options(callback: CallbackQuery):
    lead_id = int(callback.data.replace("lead_remind_", ""))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏱️ 1 soatdan keyin", callback_data=f"setrem_{lead_id}_60"),
            InlineKeyboardButton(text="⏱️ 3 soatdan keyin", callback_data=f"setrem_{lead_id}_180")
        ],
        [
            InlineKeyboardButton(text="☀️ Ertaga ertalab (10:00)", callback_data=f"setrem_{lead_id}_tommorning"),
            InlineKeyboardButton(text="🌆 Ertaga kechki payt (16:00)", callback_data=f"setrem_{lead_id}_tomevening")
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"lead_back_{lead_id}")]
    ])
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("setrem_"))
async def process_save_reminder(callback: CallbackQuery):
    parts = callback.data.split("_")
    lead_id = int(parts[1])
    time_code = parts[2]

    now = datetime.now()
    if time_code == "60":
        remind_at = now + timedelta(hours=1)
        note = "1 soatdan keyin qayta bog'lanish"
    elif time_code == "180":
        remind_at = now + timedelta(hours=3)
        note = "3 soatdan keyin qayta bog'lanish"
    elif time_code == "tommorning":
        remind_at = now + timedelta(days=1)
        note = "Ertaga ertalab bog'lanish"
    else:
        remind_at = now + timedelta(days=1, hours=6)
        note = "Ertaga kechki payt bog'lanish"

    await crud.create_reminder(lead_id, callback.from_user.id, remind_at, note)
    await crud.update_lead_status(lead_id, "KEYINROQ", callback.from_user.id, note)

    await callback.answer("⏰ Eslatma muvaffaqiyatli saqlandi!", show_alert=True)
    await callback.message.edit_reply_markup(
        reply_markup=get_admin_lead_keyboard(lead_id)
    )


# --- /tour_add TUR QO'SHISH ---
@router.message(Command("tour_add"))
async def cmd_tour_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.tour_destination)
    await message.answer("Yangi tur yo'nalishini kiriting (Masalan: Turkiya, Dubai, Misr):")


@router.message(AdminStates.tour_destination, F.text)
async def process_tour_add_dest(message: Message, state: FSMContext):
    await state.update_data(destination=message.text.strip())
    await state.set_state(AdminStates.tour_title)
    await message.answer("Tur sarlavhasi (Masalan: Antaliya 7 kunlik hordiq):")


@router.message(AdminStates.tour_title, F.text)
async def process_tour_add_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminStates.tour_price)
    await message.answer("Tur narxini USD da kiriting (Masalan: 450):")


@router.message(AdminStates.tour_price, F.text)
async def process_tour_add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip())
    except ValueError:
        await message.answer("Iltimos, faqat raqam kiriting (Masalan: 450):")
        return
    await state.update_data(price=price)
    await state.set_state(AdminStates.tour_description)
    await message.answer("Tur tavsifini yozing:")


@router.message(AdminStates.tour_description, F.text)
async def process_tour_add_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AdminStates.tour_included)
    await message.answer("Narx ichiga nimalar kiradi? (Aviachipta, Mehmonxona 5*, Transfer va h.k.):")


@router.message(AdminStates.tour_included, F.text)
async def process_tour_add_included(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    tour = await crud.add_tour(
        destination=data["destination"],
        title=data["title"],
        price_usd=data["price"],
        description=data["description"],
        whats_included=message.text.strip()
    )
    await message.answer(f"✅ Yangi tur muvaffaqiyatli qo'shildi! (ID: {tour.id})")


# --- /faq_add FAQ QO'SHISH ---
@router.message(Command("faq_add"))
async def cmd_faq_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.faq_country)
    await message.answer("Qaysi davlat uchun FAQ? (Masalan: Britaniya, AQSh, Shengen):")


@router.message(AdminStates.faq_country, F.text)
async def process_faq_add_c(message: Message, state: FSMContext):
    await state.update_data(country=message.text.strip())
    await state.set_state(AdminStates.faq_topic)
    await message.answer("Mavzu sarlavhasi (Masalan: Kerakli hujjatlar):")


@router.message(AdminStates.faq_topic, F.text)
async def process_faq_add_t(message: Message, state: FSMContext):
    await state.update_data(topic=message.text.strip())
    await state.set_state(AdminStates.faq_content)
    await message.answer("To'liq ma'lumot matnini kiriting:")


@router.message(AdminStates.faq_content, F.text)
async def process_faq_add_cnt(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await crud.add_faq(data["country"], data["topic"], message.text.strip())
    await message.answer("✅ Yangi ma'lumot (FAQ) saqlandi!")


# --- /result_add NATIJA QO'SHISH ---
@router.message(Command("result_add"))
async def cmd_result_add(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.result_name)
    await message.answer("Mijoz ismi (Masalan: Jamshid M.):")


@router.message(AdminStates.result_name, F.text)
async def process_res_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminStates.result_country)
    await message.answer("Davlat (Masalan: Buyuk Britaniya):")


@router.message(AdminStates.result_country, F.text)
async def process_res_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text.strip())
    await state.set_state(AdminStates.result_service)
    await message.answer("Xizmat turi (Masalan: Sayyohlik vizasi):")


@router.message(AdminStates.result_service, F.text)
async def process_res_service(message: Message, state: FSMContext):
    await state.update_data(service=message.text.strip())
    await state.set_state(AdminStates.result_content)
    await message.answer("Mijoz fikri yoki natija tavsifi:")


@router.message(AdminStates.result_content, F.text)
async def process_res_content(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await crud.add_result(
        full_name=data["name"],
        country=data["country"],
        service=data["service"],
        content=message.text.strip()
    )
    await message.answer("✅ Natija muvaffaqiyatli qo'shildi!")


# --- /broadcast HAMMAGA XABAR YUBORISH ---
@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminStates.broadcast_text)
    await message.answer("Barcha bot foydalanuvchilariga yuboriladigan xabarni kiriting:")


@router.message(AdminStates.broadcast_text, F.text)
async def process_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    broadcast_msg = message.text
    await state.clear()

    async with crud.AsyncSessionLocal() as session:
        from sqlalchemy import select
        from database.models import User
        users = (await session.execute(select(User.id))).scalars().all()

    await message.answer(f"📢 Xabar {len(users)} ta foydalanuvchiga yuborilmoqda...")

    sent_count = 0
    fail_count = 0
    for uid in users:
        try:
            await bot.send_message(chat_id=uid, text=broadcast_msg, parse_mode="HTML")
            sent_count += 1
            await asyncio.sleep(0.05)  # Telegram API limit (30 msg/sec)
        except Exception:
            fail_count += 1

    await message.answer(
        f"✅ <b>Xabar yuborish yakunlandi!</b>\n\n"
        f"Muvaffaqiyatli: {sent_count} ta\n"
        f"Yetib bormadi (bloklagan): {fail_count} ta",
        parse_mode="HTML"
    )


# --- /id VA /group_id BUYRUG'I ---
@router.message(Command("id", "group_id", "myid"))
async def cmd_get_id(message: Message):
    chat_type = message.chat.type
    chat_id = message.chat.id
    user_id = message.from_user.id

    if chat_type in ["group", "supergroup"]:
        text = (
            f"👥 <b>Guruh ma'lumotlari:</b>\n"
            f"🏷️ <b>Guruh nomi:</b> {message.chat.title}\n"
            f"🆔 <b>Guruh ID:</b> <code>{chat_id}</code>\n"
            f"👤 <b>Sizning ID:</b> <code>{user_id}</code>\n\n"
            f"📌 Ushbu guruhga bot arizalarini yo'naltirish uchun <code>/set_group</code> buyrug'ini yuboring."
        )
    else:
        text = (
            f"👤 <b>Foydalanuvchi ma'lumotlari:</b>\n"
            f"🆔 <b>Sizning Telegram ID:</b> <code>{user_id}</code>\n"
            f"💬 <b>Chat ID:</b> <code>{chat_id}</code>"
        )
    await message.reply(text, parse_mode="HTML")


# --- /set_group GURUHNI ULASH BUYRUG'I ---
@router.message(Command("set_group", "connect_group"))
async def cmd_set_admin_group(message: Message, bot: Bot):
    if message.chat.type not in ["group", "supergroup"]:
        await message.reply("⚠️ Ushbu buyruqni arizalar kelishi kerak bo'lgan Telegram guruhida yuboring.")
        return

    # Super admin yoki guruh adminligi tekshiruvi
    user_is_super = is_admin(message.from_user.id)
    if not user_is_super:
        try:
            member = await bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ["creator", "administrator"]:
                await message.reply("⛔ Ushbu amalni bajarish uchun siz guruh administratori yoki bot super admini bo'lishingiz kerak.")
                return
        except Exception:
            await message.reply("⛔ Ruxsat tekshirishda xatolik yuz berdi.")
            return

    # Bot guruhda admin ekanligini tekshirish
    try:
        me = await bot.get_me()
        bot_member = await bot.get_chat_member(message.chat.id, me.id)
        if bot_member.status != "administrator":
            await message.reply(
                "⚠️ <b>Eslatma:</b> Bot guruhda xabarlarni to'sqinliksiz yuborishi uchun botni guruhga <b>ADMIN (administrator)</b> qilib tayinlashingiz shart!\n"
                "Iltimos, guruh sozlamalaridan botga adminlik huquqini bering.",
                parse_mode="HTML"
            )
    except Exception:
        pass

    update_admin_group_id(message.chat.id)

    # Guruh komandalarini o'rnatishga urinish
    try:
        from bot.utils.commands import set_bot_commands
        await set_bot_commands(bot)
    except Exception:
        pass

    await message.reply(
        f"✅ <b>Guruh muvaffaqiyatli ulandi!</b>\n\n"
        f"🏷️ <b>Guruh nomi:</b> {message.chat.title}\n"
        f"🆔 <b>Guruh ID:</b> <code>{message.chat.id}</code>\n\n"
        f"📩 Endi mijozlar botdan qoldirgan barcha arizalar (Viza, O'qish, Tur, Konsultatsiya) to'g'ridan-to'g'ri ushbu guruhga keladi va menejerlar shu yerdan turib arizalarni qabul qilishi mumkin!",
        parse_mode="HTML"
    )


# --- BOT GURUHGA QO'SHILGANDA SALOMLASHISH ---
@router.message(F.new_chat_members)
async def on_new_chat_members(message: Message, bot: Bot):
    me = await bot.get_me()
    for member in message.new_chat_members:
        if member.id == me.id:
            await message.answer(
                f"👋 <b>Assalomu alaykum! {config.COMPANY_NAME} boti guruhga qo'shildi.</b>\n\n"
                f"🆔 <b>Ushbu guruh ID si:</b> <code>{message.chat.id}</code>\n\n"
                f"📌 <b>Arizalar shu guruhga kelishi uchun:</b>\n"
                f"1️⃣ Botni ushbu guruhga <b>ADMIN</b> (administrator) qiling.\n"
                f"2️⃣ Guruhda <code>/set_group</code> buyrug'ini yuboring.\n\n"
                f"Shundan so'ng bot arizalarni qabul qilishga tayyor bo'ladi!",
                parse_mode="HTML"
            )
            break

