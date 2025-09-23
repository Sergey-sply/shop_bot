from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.product import ProductRepositoryPort
from src.database.models import Product, Cart
from src.application.schemas.product import ProductSchemaCreate, CategoryProductsListSchema, ProductBaseInfo, \
    ProductFullInfo, ProductListSchema, ProductUpdate


class ProductRepository(ProductRepositoryPort):

    async def create_product(self, product_data: ProductSchemaCreate, session: AsyncSession) -> ProductFullInfo | None:
        product = Product(**product_data.model_dump())
        session.add(product)
        await session.flush()
        await session.refresh(product)
        return ProductFullInfo.model_validate(product)

    async def get_product_list_by_category_id(
        self,
        category_id: int,
        page: int,
        per_page: int,
        session: AsyncSession | None,
    ) -> CategoryProductsListSchema | None:
        query = select(
            Product.id,
            Product.name,
            Product.price,
            Product.quantity
        ).where(
            Product.category_id == category_id,
            Product.quantity > 0
        ).limit(per_page).offset((page-1)*per_page)

        result = await session.execute(query)

        rows = result.all()

        if rows:
            count_stmt = (
                select(func.count()).select_from(Product)
                .where(Product.category_id == category_id, Product.quantity > 0)
            )
            total_count = await session.scalar(count_stmt)

            products = CategoryProductsListSchema(
                category_id=category_id,
                page=page,
                total_count=total_count,
                products=[
                    ProductBaseInfo(
                        id=row.id,
                        name=row.name,
                        price=row.price,
                        quantity=row.quantity
                    ) for row in rows
                ]
            )

            return products

        return None

    async def get_product_info(self, product_id: int, session: AsyncSession) -> ProductFullInfo | None:
        query = select(Product).where(Product.id == product_id)
        result = await session.execute(query)
        product = result.scalar_one_or_none()
        if product:
            return ProductFullInfo.model_validate(product)
        return None

    async def decrease_product_stock_batch(self, user_id: int, session: AsyncSession) -> None:
        stmt = (
            update(Product)
            .values(quantity=Product.quantity - Cart.quantity)
            .where(
                Product.id == Cart.product_id,
                Cart.user_id == user_id,
            )
        )

        await session.execute(stmt)

    async def get_product_list(self, page: int, per_page: int, session: AsyncSession) -> ProductListSchema | None:
        query = select(
            Product.id,
            Product.name,
            Product.price,
            Product.quantity
        ).limit(per_page).offset((page-1)*per_page)

        result = await session.execute(query)
        products = result.all()

        if products:
            count_stmt = select(func.count()).select_from(Product)
            total_count = await session.scalar(count_stmt)
            return ProductListSchema(
                page=page,
                total_count=total_count,
                products=[
                    ProductBaseInfo(
                        id=row.id,
                        name=row.name,
                        price=row.price,
                        quantity=row.quantity
                    ) for row in products
                ]
            )


    async def update_product(
        self,
        product_id: int,
        data: ProductUpdate,
        session: AsyncSession
    ) -> ProductFullInfo | None:

        stmt = (
            update(Product)
            .where(Product.id == product_id)
            .values(
                {
                    data.field: data.value
                }
            )
            .returning(Product)
        )

        res = await session.execute(stmt)
        updated = res.scalar_one_or_none()

        if updated is None:
            return None

        return ProductFullInfo.model_validate(updated, from_attributes=True)



