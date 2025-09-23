from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.delivery_method import DeliveryMethodRepositoryPort
from src.database.models import DeliveryMethod
from src.application.schemas.delivery import DeliveryMethodSchema


class DeliveryMethodRepository(DeliveryMethodRepositoryPort):

    async def create_delivery_method(self, delivery_name: str, session: AsyncSession) -> int | None:
        delivery_method = DeliveryMethod(
            name=delivery_name
        )
        session.add(delivery_method)
        await session.flush()
        await session.refresh(delivery_method)
        return delivery_method.id

    async def get_delivery_methods(self, session: AsyncSession) -> list[DeliveryMethodSchema] | None:
        query = select(DeliveryMethod.id, DeliveryMethod.name)
        result = await session.execute(query)

        methods = result.all()
        if methods:
            return [
                DeliveryMethodSchema(
                    id=row.id,
                    name=row.name
                ) for row in methods
            ]
        return None

