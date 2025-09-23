from typing import Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.category import CategorySchemaCreate, CategoryListSchema

@runtime_checkable
class CategoryServicePort(Protocol):

    async def create_category(self, category_data: CategorySchemaCreate, session: AsyncSession | None  = None) -> int | None: ...

    async def get_category_list( self, page: int, per_page: int, session: AsyncSession | None = None) -> CategoryListSchema | None: ...
