from aiogram.filters import Filter
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineQuery
from dishka import FromDishka

from src.application.ports.services.user import UserServicePort
from src.config.settings import settings

class RoleFilter(Filter):

    def __init__(
        self,
        required_role: str,
    ) -> None:
        self.required_role = required_role

    async def __call__(
        self,
        event: TelegramObject,
        user_service: UserServicePort = FromDishka[UserServicePort]
    ) -> bool:

        user_id = self._extract_user_id(event)
        if user_id is None:
            return False

        if user_id == settings.ADMIN_TG_ID:
            return True

        roles = await user_service.get_user_roles_by_id(
            user_id=user_id
        )
        if roles:
            return self.required_role in roles
        return False

    def _extract_user_id(self, event: TelegramObject) -> int | None:

        if isinstance(event, Message):
            return event.from_user.id if event.from_user else None

        if isinstance(event, CallbackQuery):
            return event.from_user.id if event.from_user else None

        if isinstance(event, InlineQuery):
            return event.from_user.id if event.from_user else None
        return None