from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.delivery_method import DeliveryMethodRepositoryPort
from src.application.ports.services.delivery_method import DeliveryMethodServicePort
from src.infrastructure.database.decorators import use_session
from src.application.schemas.delivery import DeliveryMethodSchema


class DeliveryMethodService(DeliveryMethodServicePort):
    def __init__(self, delivery_method_repository: DeliveryMethodRepositoryPort):
        self.repo = delivery_method_repository

    @use_session
    async def create_delivery_method(self, delivery_name: str, session: AsyncSession | None = None) -> int | None:
        return await self.repo.create_delivery_method(delivery_name, session)

    @use_session
    async def get_delivery_methods(self, session: AsyncSession | None = None) -> list[DeliveryMethodSchema] | None:
        return await self.repo.get_delivery_methods(session)