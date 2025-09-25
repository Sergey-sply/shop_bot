from structlog import get_logger

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.ports.services.order import OrderServicePort
from src.core.enums.order import OrderStatus
from src.application.schemas.order import OrderFullInfoSchema

log = get_logger(__name__)

class UpdateOrderStatusUseCase:
    def __init__(
        self,
        order_service: OrderServicePort,
        session_maker: async_sessionmaker[AsyncSession]
    ):
        self.__order_service = order_service
        self.__session_maker = session_maker

    async def __call__(self, order_id: str, status: OrderStatus) -> OrderFullInfoSchema | None:
        log.info("Try to update order status", order_id=order_id)
        async with self.__session_maker() as session:
            async with session.begin():
                try:
                    await self.__order_service.change_order_status(
                        order_id=order_id,
                        status=status,
                        session=session
                    )
                    order_full_info = await self.__order_service.get_order_full_info(
                        order_id=order_id,
                        session=session
                    )
                    log.info("Order status success updated", order_id=order_id, status=status.value)
                    return order_full_info

                except Exception as e:
                    log.error("Error on UpdateOrderStatusUseCase", exc_info=True)
                    raise e

