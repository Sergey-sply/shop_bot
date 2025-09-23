from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.user import UserRepositoryPort
from src.application.ports.services.user import UserServicePort
from src.infrastructure.database.decorators import use_session
from src.application.schemas.user import UserSchemaCreate


class UserService(UserServicePort):
    def __init__(self, user_repo: UserRepositoryPort):
        self.repo = user_repo

    @use_session
    async def create_user(self, user_data: UserSchemaCreate, session: AsyncSession | None = None) -> int:
        return await self.repo.create_user(user_data=user_data, session=session)

    @use_session
    async def exist_by_id(self, user_id: int, session: AsyncSession | None = None) -> bool:
        return await self.repo.exist_by_id(user_id=user_id, session=session)

    @use_session
    async def get_user_roles_by_id(self, user_id: int, session: AsyncSession | None = None) -> list[str] | None:
        return await self.repo.get_user_roles_by_id(user_id=user_id, session=session)