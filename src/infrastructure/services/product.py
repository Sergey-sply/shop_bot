from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.product import ProductRepositoryPort
from src.application.ports.services.product import ProductServicePort
from src.infrastructure.database.decorators import use_session
from src.application.schemas.product import ProductSchemaCreate, CategoryProductsListSchema, ProductFullInfo, \
    ProductListSchema, ProductUpdate


class ProductService(ProductServicePort):
    def __init__(self, product_repository: ProductRepositoryPort):
        self.repo = product_repository

    @use_session
    async def create_product(self, product_data: ProductSchemaCreate, session: AsyncSession | None = None) -> ProductFullInfo | None:
        return await self.repo.create_product(product_data, session)

    @use_session
    async def get_product_list_by_category_id(
        self,
        category_id: int,
        page: int,
        per_page: int,
        session: AsyncSession | None = None,
    ) -> CategoryProductsListSchema | None:
        return await self.repo.get_product_list_by_category_id(
            category_id=category_id,
            page=page,
            per_page=per_page,
            session=session
        )

    @use_session
    async def get_product_info(self, product_id: int, session: AsyncSession | None = None) -> ProductFullInfo | None:
        return await self.repo.get_product_info(product_id, session)

    @use_session
    async def decrease_product_stock_batch(self, user_id: int, session: AsyncSession) -> None:
        await self.repo.decrease_product_stock_batch(user_id, session)

    @use_session
    async def get_product_list(self, page: int, per_page: int, session: AsyncSession | None = None) -> ProductListSchema | None:
        return await self.repo.get_product_list(
            page=page,
            per_page=per_page,
            session=session
        )

    @use_session
    async def update_product(
        self,
        product_id: int,
        data: ProductUpdate,
        session: AsyncSession | None = None
    ) -> ProductFullInfo | None:
        return await self.repo.update_product(
            product_id=product_id,
            data=data,
            session=session
        )