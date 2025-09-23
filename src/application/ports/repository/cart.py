from typing import Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.cart import CartSchema, UserCartSchema


@runtime_checkable
class CartRepositoryPort(Protocol):

    async def create_cart(self, user_id: int, product_id, quantity: int, session: AsyncSession) -> int | None: ...

    async def get_user_cart(self, user_id: int, page: int, session: AsyncSession, per_page: int) -> UserCartSchema | None: ...

    async def get_cart_item_info(self, cart_id: int, session: AsyncSession) -> CartSchema | None: ...

    async def get_user_cart_cost(self, user_id: int, session: AsyncSession) -> int: ...

    async def change_quantity(self, cart_id: int, quantity: int, session: AsyncSession) -> int: ...

    async def delete_cart_by_id(self, cart_id: int, session: AsyncSession) -> None: ...

    async def delete_all_user_carts(self, user_id: int, session: AsyncSession) -> None: ...


