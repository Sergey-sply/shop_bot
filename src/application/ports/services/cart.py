from typing import Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.schemas.cart import UserCartSchema, CartSchema

@runtime_checkable
class CartServicePort(Protocol):

    async def create_cart(
        self,
        user_id: int,
        product_id: int,
        quantity: int,
        session: AsyncSession | None = None
    ) -> int | None: ...

    async def get_user_cart(
        self,
        user_id: int,
        page: int,
        per_page: int,
        session: AsyncSession | None = None,
    ) -> UserCartSchema | None: ...

    async def get_user_cart_cost( self, user_id: int, session: AsyncSession | None = None) -> int: ...

    async def get_cart_item_info(self, cart_id: int, session: AsyncSession | None = None) -> CartSchema | None: ...

    async def change_quantity(self, cart_id: int, quantity: int, session: AsyncSession | None = None) -> int: ...

    async def delete_cart_by_id(self, cart_id: int, session: AsyncSession | None = None) -> None: ...

    async def delete_all_user_carts(self, user_id: int, session: AsyncSession | None = None) -> None: ...