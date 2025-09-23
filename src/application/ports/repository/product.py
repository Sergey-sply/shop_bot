from typing import Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.product import ProductSchemaCreate, CategoryProductsListSchema, \
    ProductFullInfo, ProductListSchema, ProductUpdate


@runtime_checkable
class ProductRepositoryPort(Protocol):
    async def create_product(self, product_data: ProductSchemaCreate, session: AsyncSession) -> ProductFullInfo | None: ...

    async def get_product_list_by_category_id(
        self,
        category_id: int,
        page: int,
        per_page: int,
        session: AsyncSession | None,
    ) -> CategoryProductsListSchema | None: ...

    async def get_product_info(self, product_id: int, session: AsyncSession) -> ProductFullInfo | None: ...

    async def decrease_product_stock_batch(self, user_id: int, session: AsyncSession) -> None: ...

    async def get_product_list(self, page: int, per_page: int, session: AsyncSession) -> ProductListSchema | None: ...

    async def update_product( self, product_id: int, data: ProductUpdate, session: AsyncSession) -> ProductFullInfo | None: ...



