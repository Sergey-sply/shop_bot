from sqlalchemy import select, insert, literal, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.application.ports.repository.order import OrderRepositoryPort
from src.core.enums.order import OrderStatus
from src.database.models import Cart, Product, Order, DeliveryMethod, OrderItem
from src.core.exceptions.order import OutOfStock, EmptyUserCart
from src.application.schemas.order import OrderSchemaCreate, OrderFullInfoSchema, OrderItemSchema, OrderListSchema


class OrderRepository(OrderRepositoryPort):

    async def create_order(self, order_data: OrderSchemaCreate, session: AsyncSession) -> str | None:
        # 1) lock user cart and product row
        user_cart = (
            select(
                Cart.product_id,
                Cart.quantity.label("qty"),
                Product.price,
                Product.quantity.label("stock"),
                Product.name
            )
            .join(Product, Product.id == Cart.product_id)
            .where(Cart.user_id == order_data.user_id)
            .with_for_update()  # lock
        )
        rows = (await session.execute(user_cart)).all()

        # check empty user cart
        if not rows:
            raise EmptyUserCart(user_id=order_data.user_id)

        # 2) check stock
        out_of_stock = [
            {"product_name": p_name, "stock": stock, "need": qty}
            for (pid, qty, price, stock, p_name) in rows
            if stock is not None and stock < qty
        ]
        if out_of_stock:
            raise OutOfStock(out_of_stock)

        order = Order(
            user_id=order_data.user_id,
            delivery_method_id=order_data.delivery_method_id,
            status=OrderStatus.created,
            client_name=order_data.client_name,
            client_number=order_data.client_number,
            client_address=order_data.client_address,
        )
        session.add(order)
        await session.flush()
        await session.refresh(order)

        return str(order.id)

    async def insert_order_items_from_cart(self, order_id: str, user_id: int, session: AsyncSession):
        cart_items = (
            select(
                literal(order_id, type_=PG_UUID(as_uuid=True)),
                Cart.product_id,
                Cart.quantity,
                Product.price,
            )
            .select_from(Cart)
            .join(Product, Product.id == Cart.product_id)
            .where(Cart.user_id == user_id)
        )
        await session.execute(
            insert(OrderItem).from_select(
                ["order_id", "product_id", "quantity", "unit_price"],
                cart_items,
            )
        )

    async def change_order_status(self, order_id: str, status: OrderStatus, session: AsyncSession) -> None:
        stmt = update(Order).values(status=status.value).where(Order.id == order_id)
        await session.execute(stmt)


    async def get_order_full_info(self, order_id: str, session: AsyncSession) -> OrderFullInfoSchema | None:
        query = (
            select(
                Order.user_id,
                Order.client_name,
                Order.client_number,
                Order.client_address,
                Order.status,
                DeliveryMethod.name.label("delivery_method_name"),

                Product.name.label("product_name"),
                OrderItem.quantity,
                OrderItem.unit_price,
            )
            .join(DeliveryMethod, DeliveryMethod.id == Order.delivery_method_id)
            .outerjoin(OrderItem, OrderItem.order_id == Order.id)
            .outerjoin(Product, Product.id == OrderItem.product_id)
            .where(Order.id == order_id)
        )

        result = await session.execute(query)
        rows = result.all()
        if not rows:
            return None

        return OrderFullInfoSchema(
            user_id=rows[0].user_id,
            order_id=order_id,
            order_status=rows[0].status,
            delivery_method_name=rows[0].delivery_method_name,
            client_name=rows[0].client_name,
            client_number=rows[0].client_number,
            client_address=rows[0].client_address,
            items=[
                OrderItemSchema(
                    product_name=row.product_name,
                    quantity=row.quantity,
                    unit_price=row.unit_price,
                ) for row in rows
            ],
        )

    async def get_user_orders(self, user_id: int, session: AsyncSession | None) -> list[str] | None:
        query = select(Order.id).where(Order.user_id == user_id)
        result = await session.execute(query)
        order_ids = result.scalars().all()
        return [str(order_id) for order_id in order_ids] or None


    async def get_orders(self, page: int, per_page: int, session: AsyncSession) -> OrderListSchema | None:
        query = select(Order.id)
        result = await session.execute(query)
        order_ids = result.scalars().all()
        if not order_ids:
            return None

        return OrderListSchema(
            page=page,
            per_page=per_page,
            total_count=len(order_ids),
            orders=[str(order_id) for order_id in order_ids]
        )

