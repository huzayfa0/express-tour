from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards import get_main_inline_keyboard, get_main_reply_keyboard
from config import config

router = Router()

START_TEXT = (
    f"🌍 <b>Assalomu alaykum! {config.COMPANY_NAME} botiga xush kelibsiz.</b>\n\n"
    "Biz sizga yordam beramiz:\n"
    "🛂 <b>Viza olish</b> — Britaniya, AQSh, Shengen, Kanada, Avstraliya va boshqalar\n"
    "🎓 <b>Xorijda o'qish</b> — nufuzli universitetlarga qabul va viza ko'magi\n"
    "✈️ <b>Tur paketlar</b> — Turkiya, Misr, Tailand, Dubai va boshqa ajoyib yo'nalishlar\n\n"
    "👇 Kerakli xizmatni tanlang:"
)

HELP_TEXT = (
    f"ℹ️ <b>«{config.COMPANY_NAME}» boti bo'yicha qo'llanma:</b>\n\n"
    "Quyidagi tezkor buyruqlardan foydalanishingiz mumkin:\n\n"
    "🔄 /start — Botni yangitdan ishga tushirish va asosiy menyu\n"
    "🛂 /visa — Viza olish bo'yicha ariza qoldirish\n"
    "🎓 /study — Xorijda o'qish yo'nalishlari va universitetlar\n"
    "✈️ /tour — Qaynoq tur paketlar bilan tanishish\n"
    "💬 /consult — Mutaxassisdan bepul konsultatsiya olish\n"
    "📋 /status — Arizangiz holatini ET-XXXX raqami orqali tekshirish\n"
    "📍 /contact — Ofisimiz manzili, telefon va lokatsiyasi\n"
    "❌ /cancel — Har qanday amaliyotni bekor qilish\n\n"
    f"📞 Aloqa: {config.COMPANY_PHONE}\n"
    f"✈️ Telegram: {config.COMPANY_TELEGRAM}"
)

@router.message(CommandStart())
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=START_TEXT,
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard()
    )
    await message.answer(
        text="👇 Quyidagi menyu orqali ham kerakli bo'limga o'tishingiz mumkin:",
        reply_markup=get_main_reply_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        text=HELP_TEXT,
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard()
    )

@router.callback_query(F.data == "back_to_main")
async def cb_back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text=START_TEXT,
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard()
    )
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_reply_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_action")
async def cb_cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="❌ Amal bekor qilindi.\n\n" + START_TEXT,
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard()
    )
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_reply_keyboard()
    )
    await callback.answer("Amal bekor qilindi")

@router.message(Command("cancel"))
@router.message(F.text.in_(["❌ Bekor qilish", "🏠 Asosiy menyu", "🔙 Bosh menyu"]))
async def msg_cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="❌ Amal bekor qilindi.\n\n" + START_TEXT,
        parse_mode="HTML",
        reply_markup=get_main_inline_keyboard()
    )
    await message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_reply_keyboard()
    )
