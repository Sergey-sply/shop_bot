from typing import runtime_checkable, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.user import UserSchemaCreate

@runtime_checkable
class UserServicePort(Protocol):

    async def create_user(self, user_data: UserSchemaCreate, session: AsyncSession | None = None) -> int: ...

    async def exist_by_id(self, user_id: int, session: AsyncSession | None = None) -> bool: ...

    async def get_user_roles_by_id(self, user_id: int, session: AsyncSession | None = None) -> list[str] | None: ...