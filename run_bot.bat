@echo off
title Express Tour Telegram Bot
chcp 65001 > nul
echo ====================================================
echo        EXPRESS TOUR TELEGRAM BOT & MINI-CRM
echo ====================================================
echo.

if not exist .env (
    echo [OGOHLANTIRISH] .env fayli topilmadi. .env.example dan nusxa olinmoqda...
    copy .env.example .env
    echo Iltimos, .env faylini ochib BOT_TOKEN va ADMIN_GROUP_ID ni kiriting!
    pause
    exit /b
)

echo Python kutubxonalari tekshirilmoqda...
python -m pip install -r requirements.txt --quiet

echo.
echo Bot ishga tushirilmoqda...
python main.py
pause
