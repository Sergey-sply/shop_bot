from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.category import CategoryRepositoryPort
from src.application.ports.services.category import CategoryServicePort
from src.infrastructure.database.decorators import use_session
from src.application.schemas.category import CategorySchemaCreate, CategoryListSchema


class CategoryService(CategoryServicePort):
    def __init__(self, category_repository: CategoryRepositoryPort):
        self.repo = category_repository

    @use_session
    async def create_category(self, category_data: CategorySchemaCreate, session: AsyncSession | None = None) -> int | None:
        return await self.repo.create_category(category_data, session)

    @use_session
    async def get_category_list(
        self,
        page: int,
        per_page: int,
        session: AsyncSession | None = None,
    ) -> CategoryListSchema | None:
        return await self.repo.get_category_list(
            page=page,
            per_page=per_page,
            session=session,
        )
