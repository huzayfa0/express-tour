import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from config import config
from database import crud
from bot.keyboards.inline import get_admin_lead_keyboard

logger = logging.getLogger(__name__)

async def check_and_send_reminders(bot: Bot):
    try:
        reminders = await crud.get_pending_reminders()
        for r in reminders:
            lead = r.lead
            if not lead:
                await crud.mark_reminder_sent(r.id)
                continue

            text = (
                f"⏰ <b>ESLATMA | Mijoz bilan bog'lanish vaqti bo'ldi!</b>\n\n"
                f"📌 Ariza: <b>#{lead.lead_number}</b>\n"
                f"👤 Mijoz: <b>{lead.name or 'Noma\'lum'}</b>\n"
                f"📱 Telefon: <b>{lead.phone or 'Mavjud emas'}</b>\n"
                f"🌍 Xizmat/Davlat: <b>{lead.service.capitalize()} | {lead.country or ''}</b>\n"
                f"📝 Eslatma izohi: <i>{r.note or 'Belgilangan vaqt bo\'yicha qayta qo\'ng\'iroq'}</i>\n\n"
                f"Iltimos, mijoz bilan zudlik bilan bog'laning va statusni yangilang!"
            )

            # Send to admin group
            if config.ADMIN_GROUP_ID:
                try:
                    await bot.send_message(
                        chat_id=config.ADMIN_GROUP_ID,
                        text=text,
                        parse_mode="HTML",
                        reply_markup=get_admin_lead_keyboard(lead.id)
                    )
                except Exception as e:
                    logger.error(f"Failed to send reminder to admin group: {e}")

            # Send to assigned manager directly if available
            if r.manager_id:
                try:
                    await bot.send_message(
                        chat_id=r.manager_id,
                        text=text,
                        parse_mode="HTML",
                        reply_markup=get_admin_lead_keyboard(lead.id)
                    )
                except Exception as e:
                    logger.warning(f"Could not send PM to manager {r.manager_id}: {e}")

            await crud.mark_reminder_sent(r.id)
    except Exception as e:
        logger.error(f"Error in check_and_send_reminders: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(
        check_and_send_reminders,
        "interval",
        minutes=1,
        args=[bot]
    )
    return scheduler
