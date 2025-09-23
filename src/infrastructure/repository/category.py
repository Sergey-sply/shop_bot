from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.category import CategoryRepositoryPort
from src.database.models import Category
from src.application.schemas.category import CategorySchemaCreate, CategoryListSchema, CategoryBaseInfo


class CategoryRepository(CategoryRepositoryPort):

    async def create_category(self, category_data: CategorySchemaCreate, session: AsyncSession) -> int | None:
        category = Category(**category_data.model_dump())
        session.add(category)
        await session.flush()
        await session.refresh(category)
        return category.id

    async def get_category_list(self, page: int, per_page: int, session: AsyncSession) -> CategoryListSchema | None:
        query = select(Category.id, Category.name).limit(per_page).offset((page-1)*per_page)
        result = await session.execute(query)

        rows = result.all()

        if rows:
            count_stmt = select(func.count()).select_from(Category)
            total_count = await session.scalar(count_stmt)

            categories = CategoryListSchema(
                categories=[
                    CategoryBaseInfo(
                        id=row.id,
                        name=row.name
                    ) for row in rows
                ],
                page=page,
                total_count=total_count
            )

            return categories
        return None