from sqlalchemy import select, update, delete, func, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.application.ports.repository.cart import CartRepositoryPort
from src.database.models import Cart, Product
from src.application.schemas.cart import UserCartSchema, CartSchema


class CartRepository(CartRepositoryPort):

    async def create_cart(self, user_id: int, product_id, quantity: int, session: AsyncSession) -> int | None:
        stmt = pg_insert(Cart).values(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity
        ).on_conflict_do_nothing(
            constraint="_user_product_cart_uc" # cart exist
        ).returning(Cart.id)

        res = await session.execute(stmt)
        row = res.first()
        if row:
            return row.id
        return None

    async def get_user_cart(
        self,
        user_id: int,
        page: int,
        session: AsyncSession,
        per_page: int
    ) -> UserCartSchema | None:
        query = (
            select(
                Cart.id,
                Cart.product_id,
                Cart.quantity,
                Product.price,
                Product.name
            )
            .join(Product, Product.id == Cart.product_id)
            .where(Cart.user_id == user_id)
            .limit(per_page).offset((page-1)*per_page)
        )
        result = await session.execute(query)
        rows = result.all()

        if rows:
            count_stmt = (
                select(
                    func.count(Cart.id).label("total_count"),
                    func.coalesce(func.sum(Cart.quantity * Product.price), 0).label("total_amount"),
                )
                .select_from(Cart)
                .join(Product, Product.id == Cart.product_id)
                .where(Cart.user_id == user_id)
            )

            total_count, total_amount = (await session.execute(count_stmt)).one()

            return UserCartSchema(
                page=page,
                total_count=total_count,
                total_amount=total_amount,
                items=[
                    CartSchema(
                        cart_id=row.id,
                        product_id=row.product_id,
                        quantity=row.quantity,
                        unit_price=row.price,
                        name=row.name
                    ) for row in rows
                ]
            )

    async def get_cart_item_info(self, cart_id: int, session: AsyncSession) -> CartSchema | None:
        query = (
            select(
                Cart.product_id,
                Cart.quantity,
                Product.price,
                Product.name
            )
            .join(Product, Product.id == Cart.product_id)
            .where(Cart.id == cart_id)
        )

        result = await session.execute(query)
        cart = result.first()
        if cart:
            return CartSchema(
                cart_id=cart_id,
                product_id=cart.product_id,
                quantity=cart.quantity,
                unit_price=cart.price,
                name=cart.name
            )

    async def get_user_cart_cost(self, user_id: int, session: AsyncSession) -> int:
        query = (
            select(func.coalesce(func.sum(Cart.quantity * Product.price), 0))
            .select_from(join(Cart, Product, Cart.product_id == Product.id))
            .where(Cart.user_id == user_id)
        )
        total_price = await session.scalar(query)
        return total_price

    async def change_quantity(self, cart_id: int, quantity: int, session: AsyncSession) -> int:
        stmt = (
            update(Cart)
            .values(quantity=func.least(Product.quantity, Cart.quantity + quantity))
            .where(Cart.id == cart_id, Cart.product_id == Product.id, Cart.quantity + quantity >= 0)
            .returning(Cart.quantity.label("new_qty"), Product.quantity.label("stock"))
        )

        row = (await session.execute(stmt)).first()
        if not row:
            raise ValueError("Cart not exist or cart.quantity < 0")

        new_qty, stock = row.new_qty, row.stock

        if stock == 0 or new_qty == 0:
            await session.execute(delete(Cart).where(Cart.id == cart_id))
            return 0

        return new_qty

    async def delete_cart_by_id(self, cart_id: int, session: AsyncSession) -> None:
        stmt = delete(Cart).where(Cart.id == cart_id)
        await session.execute(stmt)

    async def delete_all_user_carts(self, user_id: int, session: AsyncSession) -> None:
        stmt = delete(Cart).where(Cart.user_id == user_id)
        await session.execute(stmt)


