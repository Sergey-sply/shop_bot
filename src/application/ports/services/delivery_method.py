from typing import Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.delivery import DeliveryMethodSchema

@runtime_checkable
class DeliveryMethodServicePort(Protocol):

    async def create_delivery_method(self, delivery_name: str, session: AsyncSession | None = None) -> int | None: ...

    async def get_delivery_methods(self, session: AsyncSession | None = None) -> list[DeliveryMethodSchema] | None: ...