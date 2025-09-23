from aiogram import BaseMiddleware

from typing import Any, Callable, Awaitable
from aiogram.types import TelegramObject, Message
from dishka import AsyncContainer

from src.application.use_cases.user.get_or_create import GetOrCreateUserUseCase
from src.infrastructure.logging.config import get_logger
from src.application.schemas.user import UserSchemaCreate

log = get_logger(__name__)

class AuthMiddleware(BaseMiddleware):
    def __init__(self, container: AsyncContainer):
        self.container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        message: Message = event
        user = message.from_user

        if not user:
            return await handler(event, data)

        req_container: AsyncContainer | None = data.get("dishka_container")

        get_or_create_uc: GetOrCreateUserUseCase = await req_container.get(GetOrCreateUserUseCase)
        if await get_or_create_uc(UserSchemaCreate(name=user.username, id=user.id)):
            log.info(f"New user registration", user_id=user.id)

        return await handler(event, data)
