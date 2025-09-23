from typing import runtime_checkable, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.delivery import DeliveryMethodSchema

@runtime_checkable
class DeliveryMethodRepositoryPort(Protocol):

    async def create_delivery_method(self, delivery_name: str, session: AsyncSession) -> int | None: ...

    async def get_delivery_methods(self, session: AsyncSession) -> list[DeliveryMethodSchema] | None: ...

