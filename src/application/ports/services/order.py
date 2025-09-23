from typing import Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums.order import OrderStatus
from src.application.schemas.order import OrderSchemaCreate, OrderFullInfoSchema, OrderListSchema

@runtime_checkable
class OrderServicePort(Protocol):

    async def create_order(self, order_data: OrderSchemaCreate, session: AsyncSession) -> str | None: ...

    async def insert_order_items_from_cart(self, order_id: str, user_id: int, session: AsyncSession): ...

    async def change_order_status( self, order_id: str, status: OrderStatus, session: AsyncSession | None = None) -> OrderFullInfoSchema | None: ...

    async def get_order_full_info(self, order_id: str, session: AsyncSession | None = None) -> OrderFullInfoSchema | None: ...

    async def get_user_orders(self, user_id: int, session: AsyncSession | None = None) -> list[str] | None: ...

    async def get_orders(self, page: int, per_page: int, session: AsyncSession | None  = None) -> OrderListSchema | None: ...