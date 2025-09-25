from structlog import get_logger

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.ports.services.cart import CartServicePort
from src.application.ports.services.order import OrderServicePort
from src.application.ports.services.product import ProductServicePort
from src.core.exceptions.order import OutOfStock, EmptyUserCart
from src.application.schemas.order import OrderSchemaCreate, OrderFullInfoSchema

log = get_logger(__name__)

class CreateOrderUseCase:
    def __init__(
        self,
        order_service: OrderServicePort,
        cart_service: CartServicePort,
        product_service: ProductServicePort,
        session_maker: async_sessionmaker[AsyncSession]
    ):
        self.__order_service = order_service
        self.__cart_service = cart_service
        self.__product_service = product_service
        self.__session_maker = session_maker

    async def __call__(self, order_data: OrderSchemaCreate) -> OrderFullInfoSchema | None:
        log.info("Try to create order")
        async with self.__session_maker() as session:
            async with session.begin():
                try:
                    # create order with lock cart and product rows
                    order_id = await self.__order_service.create_order(order_data, session)
                    await self.__order_service.insert_order_items_from_cart(
                        order_id=order_id,
                        user_id=order_data.user_id,
                        session=session
                    )
                    await self.__product_service.decrease_product_stock_batch(
                        user_id=order_data.user_id,
                        session=session
                    )
                    await self.__cart_service.delete_all_user_carts(
                        user_id=order_data.user_id,
                        session=session
                    )
                    order_full_info = await self.__order_service.get_order_full_info(
                        order_id=order_id,
                        session=session
                    )
                    log.info("Success create order", order_id=order_id)
                    return order_full_info

                except EmptyUserCart as euc_ex:
                    log.warning("Empty user cart on create order")
                    raise
                except OutOfStock as oos_ex:
                    log.warning("Out of stock on create order", oos_products=oos_ex.stock_ex)
                    raise
                except Exception as e:
                    log.error("Error in CreateOrderUseCase", exc_info=True)
                    raise e

