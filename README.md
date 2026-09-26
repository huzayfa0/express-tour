# Express Tour Telegram Bot & Mini-CRM

Express Tour turizm, viza va chet elda ta'lim agentligi uchun mijozlar arizalarini (lidlarni) avtomatik qabul qilish, saralash, boshqarish va kuzatish tizimi.

---

## 🚀 Imkoniyatlar

1. **🛂 Viza olish (7 qadamli FSM):**
   * Davlat, maqsad, ketish muddati, avvalgi rad javoblari tarixi, ism, telefon va qulay qo'ng'iroq vaqti.
   * Unikal ariza raqami (`#ET-XXXX`) generatsiyasi.
2. **🎓 Xorijda o'qish:**
   * Bakalavr, Magistr, Foundation, Kollej bosqichlari.
   * IELTS bali, ta'lim byudjeti va shaxsiy ma'lumotlar.
3. **✈️ Tur paketlar:**
   * Yo'nalishlar (Turkiya, Misr, Dubai, Tailand...) bo'yicha turlarni ko'rish va band qilish.
   * Admin tomonidan dinamik tur qo'shish (`/tour_add`).
4. **💬 Bepul konsultatsiya:**
   * Eng tezkor «qaynoq» lid anketasi.
5. **📋 Arizam holati:**
   * Mijoz ariza raqamini kiritib, arizasi qaysi bosqichda ekanligini (Konsultatsiya, Hujjatlar, Elchixona, Natija) real vaqtda ko'radi.
6. **⭐ Natijalar va 📚 FAQ:**
   * Foydali ma'lumotlar va viza olgan mijozlar natijalari.
7. **CRM / Admin guruhi:**
   * Yangi lid tushishi bilan admin guruhiga to'liq anketa va interaktiv tugmalar chiqadi:
     `[📞 Qo'ng'iroq qildim] [✅ Qualif] [❌ Bog'lanmadi]`
     `[📅 Konsultatsiya] [📝 Shartnoma] [🔄 Keyinroq]`
     `[🏛️ Elchixona] [🎉 Viza oldi] [❌ Yutqazildi]`
     `[👤 Menejer tayinlash]`
   * Eslatmalar tizimi (belgilangan vaqtda menejerga qayta eslatadi).
   * Status o'zgarganda mijozga ham bildirishnoma yuboriladi.
8. **Statistika va hisobotlar:**
   * `/stats` — Bugungi jami lidlar, xizmatlar, bog'lanilgan/bog'lanilmaganlar va UTM manbalari kesimi.
   * `/leads` va `/hot` — oxirgi va bog'lanilmagan arizalar.
   * `/broadcast` — barcha foydalanuvchilarga xabar tarqatish.

---

## 🛠️ O'rnatish va Ishga tushirish (Windows)

### 1. `.env` faylini sozlash
`express_tour_bot/.env` faylini oching va quyidagi qatorlarni to'ldiring:
```env
BOT_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxxxx
ADMIN_GROUP_ID=-1001234567890
SUPER_ADMIN_IDS=123456789
```

* **BOT_TOKEN:** [@BotFather](https://t.me/BotFather) dan olingan bot tokeni.
* **ADMIN_GROUP_ID:** Menejerlar yig'ilgan Telegram guruh ID si. (Guruhga botni admin qilib qo'shing va guruh ID sini [@userinfobot](https://t.me/userinfobot) orqali biling).
* **SUPER_ADMIN_IDS:** O'zingizning shaxsiy Telegram ID ingiz.

### 2. Ishga tushirish
Faqatgina **`run_bot.bat`** faylini ikki marta bosing!
Yoki terminalda:
```bash
python main.py
```

---

## 🌐 Serverda Ishga Tushirish (Linux / Ubuntu VPS)

### 1-usul: Docker orqali (Tavsiya etiladi)
```bash
# Repozitoriyani klonlash
git clone https://github.com/huzayfa0/express-tour.git
cd express-tour

# .env faylini yaratish va sozlash
cp .env.example .env
nano .env

# Docker compose orqali fon rejimida ishga tushirish
docker compose up -d --build
```

### 2-usul: Oddiy Python + systemd orqali
```bash
# 1. Klonlash
git clone https://github.com/huzayfa0/express-tour.git
cd express-tour

# 2. Virtual muhit va kutubxonalar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. .env faylni to'ldiring
cp .env.example .env
nano .env

# 4. Sinov uchun ishga tushirish:
python3 main.py

# 5. Doimiy fon xizmati (systemd):
sudo cp express_tour.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now express_tour
```

## 📊 Marketing va UTM Tracking (Deep Linking)

Har bir reklama kanalingiz uchun quyidagi ko'rinishda havola yasang:
* Instagram Bio uchun: `https://t.me/BOT_USERNAME?start=ig_bio`
* UK viza reelsi uchun: `https://t.me/BOT_USERNAME?start=ig_uk_reel`
* AQSh viza reelsi uchun: `https://t.me/BOT_USERNAME?start=ig_usa_reel`
* Target reklama uchun: `https://t.me/BOT_USERNAME?start=ads_target_1`
* Telegram kanal uchun: `https://t.me/BOT_USERNAME?start=tg_channel`

Foydalanuvchi qaysi havola orqali kirsa, bot avtomatik ushbu manbani qayd qiladi va admin guruhiga ko'rsatadi hamda `/stats` da hisoblab boradi.
