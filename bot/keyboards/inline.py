from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional
from database.models import Tour, Manager
from config import config

def get_main_inline_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🛂 Viza olish", callback_data="menu_visa"),
            InlineKeyboardButton(text="🎓 Xorijda o'qish", callback_data="menu_study")
        ],
        [
            InlineKeyboardButton(text="✈️ Tur paketlar", callback_data="menu_tour"),
            InlineKeyboardButton(text="💬 Bepul konsultatsiya", callback_data="menu_consult")
        ],
        [
            InlineKeyboardButton(text="⭐ Natijalarimiz", url=f"https://instagram.com/{config.COMPANY_INSTAGRAM.lstrip('@')}"),
            InlineKeyboardButton(text="📋 Arizam holati", callback_data="menu_status")
        ],
        [
            InlineKeyboardButton(text="📍 Manzil va aloqa", callback_data="menu_contact")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")]
    ])


# --- VISA KEYBOARDS ---
def get_visa_countries_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🇬🇧 Britaniya", callback_data="visa_c_Britaniya"),
            InlineKeyboardButton(text="🇺🇸 AQSh", callback_data="visa_c_AQSh")
        ],
        [
            InlineKeyboardButton(text="🇦🇺 Avstraliya", callback_data="visa_c_Avstraliya"),
            InlineKeyboardButton(text="🇨🇦 Kanada", callback_data="visa_c_Kanada")
        ],
        [
            InlineKeyboardButton(text="🇳🇿 Yangi Zelandiya", callback_data="visa_c_Yangi Zelandiya"),
            InlineKeyboardButton(text="🇪🇺 Shengen", callback_data="visa_c_Shengen")
        ],
        [
            InlineKeyboardButton(text="🇰🇷 Koreya", callback_data="visa_c_Koreya"),
            InlineKeyboardButton(text="🇯🇵 Yaponiya", callback_data="visa_c_Yaponiya")
        ],
        [
            InlineKeyboardButton(text="🌍 Boshqa davlat", callback_data="visa_c_boshqa")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_visa_purposes_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🏖️ Turizm", callback_data="visa_p_Turizm"),
            InlineKeyboardButton(text="🎓 O'qish", callback_data="visa_p_O'qish")
        ],
        [
            InlineKeyboardButton(text="💼 Biznes", callback_data="visa_p_Biznes"),
            InlineKeyboardButton(text="👨‍👩‍👧 Oila", callback_data="visa_p_Oila")
        ],
        [
            InlineKeyboardButton(text="🔄 Boshqa", callback_data="visa_p_Boshqa")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_timeframes_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="⚡ 1 oy ichida", callback_data="time_1 oy ichida")],
        [InlineKeyboardButton(text="📌 1–3 oy ichida", callback_data="time_1-3 oy ichida")],
        [InlineKeyboardButton(text="🗓️ 3–6 oy ichida", callback_data="time_3-6 oy ichida")],
        [InlineKeyboardButton(text="🔮 Hali aniq emas", callback_data="time_Hali aniq emas")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_visa_refusal_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="✅ Ha, bo'lgan", callback_data="refusal_yes")],
        [InlineKeyboardButton(text="❌ Yo'q, birinchi marta", callback_data="refusal_no")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_refusal_count_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="1 marta", callback_data="refcnt_1"),
            InlineKeyboardButton(text="2 marta", callback_data="refcnt_2"),
            InlineKeyboardButton(text="3+ marta", callback_data="refcnt_3+")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_convenient_time_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🌅 09:00–12:00", callback_data="ctime_09:00-12:00"),
            InlineKeyboardButton(text="☀️ 12:00–15:00", callback_data="ctime_12:00-15:00")
        ],
        [
            InlineKeyboardButton(text="🌇 15:00–18:00", callback_data="ctime_15:00-18:00"),
            InlineKeyboardButton(text="🌆 18:00–21:00", callback_data="ctime_18:00-21:00")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- STUDY KEYBOARDS ---
def get_study_stages_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🎓 Bakalavr", callback_data="study_st_Bakalavr"),
            InlineKeyboardButton(text="🎓 Magistr", callback_data="study_st_Magistr")
        ],
        [
            InlineKeyboardButton(text="📚 Foundation", callback_data="study_st_Foundation"),
            InlineKeyboardButton(text="🏛️ Kollej", callback_data="study_st_Kollej")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_study_countries_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🇬🇧 UK", callback_data="study_c_UK"),
            InlineKeyboardButton(text="🇺🇸 USA", callback_data="study_c_USA")
        ],
        [
            InlineKeyboardButton(text="🇨🇦 Canada", callback_data="study_c_Canada"),
            InlineKeyboardButton(text="🇦🇺 Australia", callback_data="study_c_Australia")
        ],
        [
            InlineKeyboardButton(text="🇰🇷 Korea", callback_data="study_c_Korea"),
            InlineKeyboardButton(text="🇪🇺 Europe", callback_data="study_c_Europe")
        ],
        [
            InlineKeyboardButton(text="🌍 Boshqa davlat", callback_data="study_c_boshqa")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_ielts_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="✅ Bor (ball kiriting)", callback_data="ielts_yes")],
        [InlineKeyboardButton(text="❌ Yo'q", callback_data="ielts_no")],
        [InlineKeyboardButton(text="⏳ Tayyorlanmoqdaman", callback_data="ielts_preparing")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_study_budget_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="💰 $3 000 gacha", callback_data="budget_$3K gacha")],
        [InlineKeyboardButton(text="💰 $3 000 – $7 000", callback_data="budget_$3-7K")],
        [InlineKeyboardButton(text="💰 $7 000 – $15 000", callback_data="budget_$7-15K")],
        [InlineKeyboardButton(text="💰 $15 000+", callback_data="budget_$15K+")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ])


# --- TOUR KEYBOARDS ---
def get_tour_destinations_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🇹🇷 Turkiya", callback_data="tour_d_Turkiya"),
            InlineKeyboardButton(text="🇪🇬 Misr", callback_data="tour_d_Misr")
        ],
        [
            InlineKeyboardButton(text="🇦🇪 Dubai (BAA)", callback_data="tour_d_Dubai"),
            InlineKeyboardButton(text="🇹🇭 Tailand", callback_data="tour_d_Tailand")
        ],
        [
            InlineKeyboardButton(text="🇪🇺 Yevropa", callback_data="tour_d_Yevropa"),
            InlineKeyboardButton(text="🔥 Barcha turlar", callback_data="tour_all")
        ],
        [
            InlineKeyboardButton(text="✍️ O'zimga mos tur so'rash", callback_data="tour_custom")
        ],
        [
            InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_tours_list_keyboard(tours: List[Tour], destination: Optional[str] = None) -> InlineKeyboardMarkup:
    keyboard = []
    for tour in tours:
        btn_text = f"✈️ {tour.title} (${tour.price_usd:,.0f})"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"tour_id_{tour.id}")])
    keyboard.append([InlineKeyboardButton(text="✍️ O'zimga mos tur so'rash", callback_data=f"tour_custom_{destination}" if destination else "tour_custom")])
    keyboard.append([InlineKeyboardButton(text="💬 Mutaxassis bilan bog'lanish", callback_data="menu_consult")])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Boshqa yo'nalishlar", callback_data="menu_tour"),
        InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_tour_detail_keyboard(tour_id: int, destination: Optional[str] = None) -> InlineKeyboardMarkup:
    back_cb = f"tour_d_{destination}" if destination else "menu_tour"
    keyboard = [
        [InlineKeyboardButton(text="📝 Ushbu turga ariza qoldirish", callback_data=f"book_tour_{tour_id}")],
        [InlineKeyboardButton(text="💬 Mutaxassisdan konsultatsiya olish", callback_data="menu_consult")],
        [
            InlineKeyboardButton(text="🔙 Turlar ro'yxati", callback_data=back_cb),
            InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_tour_people_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="👤 1 kishi", callback_data="tour_ppl_1 kishi"),
            InlineKeyboardButton(text="👥 2 kishi (juftlik)", callback_data="tour_ppl_2 kishi")
        ],
        [
            InlineKeyboardButton(text="👨‍👩‍👧 3-4 kishi (oila)", callback_data="tour_ppl_3-4 kishi"),
            InlineKeyboardButton(text="👥 5+ kishi (katta guruh)", callback_data="tour_ppl_5+ kishi")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- CONSULTATION KEYBOARDS ---
def get_consult_service_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🛂 Viza olish", callback_data="csrv_Viza"),
            InlineKeyboardButton(text="🎓 Xorijda o'qish", callback_data="csrv_O'qish")
        ],
        [
            InlineKeyboardButton(text="✈️ Tur paketlar", callback_data="csrv_Tur"),
            InlineKeyboardButton(text="🔄 Boshqa masala", callback_data="csrv_Boshqa")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- ADMIN KEYBOARDS ---
def get_admin_lead_keyboard(lead_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="📞 Qo'ng'iroq qildim", callback_data=f"lead_st_{lead_id}_ALOQA"),
            InlineKeyboardButton(text="✅ Qualif", callback_data=f"lead_st_{lead_id}_QUALIF"),
            InlineKeyboardButton(text="❌ Bog'lanmadi", callback_data=f"lead_st_{lead_id}_BOGLANMADI")
        ],
        [
            InlineKeyboardButton(text="📅 Konsultatsiya", callback_data=f"lead_st_{lead_id}_KONSULT"),
            InlineKeyboardButton(text="📝 Shartnoma", callback_data=f"lead_st_{lead_id}_SHARTNOMA"),
            InlineKeyboardButton(text="🔄 Keyinroq", callback_data=f"lead_remind_{lead_id}")
        ],
        [
            InlineKeyboardButton(text="🏛️ Elchixona", callback_data=f"lead_st_{lead_id}_ELCHIXONA"),
            InlineKeyboardButton(text="🎉 Viza oldi", callback_data=f"lead_st_{lead_id}_VIZA_OLDI"),
            InlineKeyboardButton(text="❌ Yutqazildi", callback_data=f"lead_st_{lead_id}_YUTQAZILDI")
        ],
        [
            InlineKeyboardButton(text="👤 Menejer tayinlash", callback_data=f"lead_assign_{lead_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_assign_manager_keyboard(lead_id: int, managers: List[Manager]) -> InlineKeyboardMarkup:
    keyboard = []
    for m in managers:
        keyboard.append([
            InlineKeyboardButton(text=f"👤 {m.name} ({m.role})", callback_data=f"set_mgr_{lead_id}_{m.id}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"lead_back_{lead_id}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
