from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.user import UserRepositoryPort
from src.database.models import User, Role, UserRole
from src.application.schemas.user import UserSchemaCreate


class UserRepository(UserRepositoryPort):

    async def create_user(self, user_data: UserSchemaCreate, session: AsyncSession) -> int | None:
        user = User(**user_data.model_dump())
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user.id

    async def exist_by_id(self, user_id: int, session: AsyncSession) -> bool:
        stmt = select(exists().where(
            User.id == user_id
        ))
        result = await session.execute(stmt)
        return result.scalar()

    async def get_user_roles_by_id(self, user_id: int, session: AsyncSession) -> list[str] | None:
        query = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        res = await session.execute(query)
        names = res.scalars().all()
        return names or None

    async def create_role(self, role_name: str, session: AsyncSession) -> int | None:
        role = Role(name=role_name)
        session.add(role)
        await session.flush()
        await session.refresh(role)
        return role.id

    async def create_user_role(self, role_id: int, user_id: int, session: AsyncSession) -> tuple[int, int] | None:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        session.add(user_role)
        await session.flush()
        await session.refresh(user_role)
        return user_role.user_id, user_role.role_id