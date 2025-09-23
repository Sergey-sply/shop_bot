from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repository.cart import CartRepositoryPort
from src.application.ports.services.cart import CartServicePort
from src.infrastructure.database.decorators import use_session
from src.application.schemas.cart import UserCartSchema, CartSchema


class CartService(CartServicePort):
    def __init__(self, cart_repository: CartRepositoryPort):
        self.repo = cart_repository

    @use_session
    async def create_cart(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
        session: AsyncSession | None = None
    ) -> int | None:
        return await self.repo.create_cart(user_id, product_id, quantity, session)

    @use_session
    async def get_user_cart(
        self,
        user_id: int,
        page: int,
        per_page: int,
        session: AsyncSession | None = None,
    ) -> UserCartSchema | None:
        return await self.repo.get_user_cart(
            user_id=user_id,
            page=page,
            per_page=per_page,
            session=session
        )

    @use_session
    async def get_user_cart_cost( self, user_id: int, session: AsyncSession | None = None) -> int:
        return await self.repo.get_user_cart_cost(
            user_id=user_id,
            session=session
        )

    @use_session
    async def get_cart_item_info(self, cart_id: int, session: AsyncSession | None = None) -> CartSchema | None:
        return await self.repo.get_cart_item_info(cart_id, session)

    @use_session
    async def change_quantity(self, cart_id: int, quantity: int, session: AsyncSession | None = None) -> int:
        return await self.repo.change_quantity(cart_id, quantity, session)

    @use_session
    async def delete_cart_by_id(self, cart_id: int, session: AsyncSession | None = None) -> None:
        await self.repo.delete_cart_by_id(cart_id, session)

    @use_session
    async def delete_all_user_carts(self, user_id: int, session: AsyncSession | None = None) -> None:
        await self.repo.delete_all_user_carts(user_id, session)