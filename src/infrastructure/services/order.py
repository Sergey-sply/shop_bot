from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.order import OrderRepositoryPort
from src.application.ports.services.order import OrderServicePort
from src.core.enums.order import OrderStatus
from src.infrastructure.database.decorators import use_session
from src.application.schemas.order import OrderSchemaCreate, OrderFullInfoSchema, OrderListSchema


class OrderService(OrderServicePort):
    def __init__(self, order_repository: OrderRepositoryPort):
        self.repo = order_repository

    async def create_order(self, order_data: OrderSchemaCreate, session: AsyncSession) -> str | None:
        return await self.repo.create_order(order_data=order_data, session=session)

    async def insert_order_items_from_cart(self, order_id: str, user_id: int, session: AsyncSession):
        await self.repo.insert_order_items_from_cart(order_id, user_id, session)

    @use_session
    async def change_order_status(self, order_id: str, status: OrderStatus, session: AsyncSession | None = None) -> OrderFullInfoSchema | None:
        return await self.repo.change_order_status(order_id, status, session)

    @use_session
    async def get_order_full_info(self, order_id: str, session: AsyncSession | None = None) -> OrderFullInfoSchema | None:
        return await self.repo.get_order_full_info(order_id, session)

    @use_session
    async def get_user_orders(self, user_id: int, session: AsyncSession | None = None) -> list[str] | None:
        return await self.repo.get_user_orders(user_id, session)

    @use_session
    async def get_orders(self, page: int, per_page: int, session: AsyncSession | None = None) -> OrderListSchema | None:
        return await self.repo.get_orders(
            page=page,
            per_page=per_page,
            session=session
        )