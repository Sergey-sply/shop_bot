from typing import runtime_checkable, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.category import CategorySchemaCreate, CategoryListSchema


@runtime_checkable
class CategoryRepositoryPort(Protocol):

    async def create_category(self, category_data: CategorySchemaCreate, session: AsyncSession) -> int | None: ...

    async def get_category_list(self, page: int, per_page: int, session: AsyncSession) -> CategoryListSchema | None: ...
