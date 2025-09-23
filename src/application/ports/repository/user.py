from typing import Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.user import UserSchemaCreate


@runtime_checkable
class UserRepositoryPort(Protocol):

    async def create_user(self, user_data: UserSchemaCreate, session: AsyncSession) -> int | None: ...

    async def exist_by_id(self, user_id: int, session: AsyncSession) -> bool: ...

    async def get_user_roles_by_id(self, user_id: int, session: AsyncSession) -> list[str] | None: ...

    async def create_role(self, role_name: str, session: AsyncSession) -> int | None: ...

    async def create_user_role(self, role_id: int, user_id: int, session: AsyncSession) -> tuple[int, int] | None: ...