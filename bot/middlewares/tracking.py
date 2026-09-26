from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from database import crud

class UserTrackingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        source = "direct"

        if isinstance(event, Message) and event.from_user:
            user = event.from_user
            if event.text and event.text.startswith("/start "):
                parts = event.text.split(maxsplit=1)
                if len(parts) > 1:
                    source = parts[1].strip()
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user

        if user and not user.is_bot:
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "Noma'lum"
            db_user = await crud.get_or_create_user(
                user_id=user.id,
                full_name=full_name,
                username=user.username,
                source=source
            )
            data["db_user"] = db_user
            data["user_source"] = db_user.source if db_user.source != "direct" else source

        return await handler(event, data)
