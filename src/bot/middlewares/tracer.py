from typing import Callable, Dict, Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineQuery
from structlog.contextvars import bind_contextvars, clear_contextvars
from uuid import uuid4

class TraceIDAiogramMiddleware(BaseMiddleware):
    """
    Middleware for generate and set trace_id into log chain
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = self._extract_user_id(event)
        trace_id = str(uuid4())

        bind_contextvars(trace_id=trace_id, user_id=user_id)
        try:
            return await handler(event, data)
        finally:
            clear_contextvars()


    def _extract_user_id(self, event: TelegramObject) -> int | None:

        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None

        if isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None

        if isinstance(event, InlineQuery):
            return event.from_user.id if event.from_user else None
        return None