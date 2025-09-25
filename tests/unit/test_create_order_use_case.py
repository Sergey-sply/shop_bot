import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.ports.services.cart import CartServicePort
from src.application.ports.services.order import OrderServicePort
from src.application.ports.services.product import ProductServicePort
from src.application.use_cases.order.create import CreateOrderUseCase
from src.core.enums.order import OrderStatus
from src.core.exceptions.order import OutOfStock, EmptyUserCart
from src.application.schemas.order import OrderSchemaCreate, OrderFullInfoSchema, OrderItemSchema

pytestmark = pytest.mark.asyncio


@pytest.fixture
def order_data() -> OrderSchemaCreate:
    return OrderSchemaCreate(
        user_id=7, delivery_method_id=2,
        client_name="Ivan", client_number="+123", client_address="Earth"
    )


@pytest.fixture
def make_uc(mocker):
    """
    Generating mock services, uc, async session
    """
    def _():
        order_svc: OrderServicePort = mocker.create_autospec(
            OrderServicePort, instance=True, spec_set=True
        )
        cart_svc: CartServicePort = mocker.create_autospec(
            CartServicePort, instance=True, spec_set=True
        )
        product_svc: ProductServicePort = mocker.create_autospec(
            ProductServicePort, instance=True, spec_set=True
        )

        # Mock AsyncSession as async context manager
        session = AsyncMock(spec=AsyncSession)
        session.__aenter__.return_value = session
        session.__aexit__.return_value = None

        # Mock transaction: session.begin()
        begin_cm = AsyncMock()
        begin_cm.__aenter__.return_value = None
        begin_cm.__aexit__.return_value = None
        session.begin.return_value = begin_cm


        session_maker = MagicMock(spec=async_sessionmaker[AsyncSession])
        session_maker.return_value = session

        uc = CreateOrderUseCase(order_svc, cart_svc, product_svc, session_maker)
        return uc, order_svc, cart_svc, product_svc, session, session_maker
    return _


async def test_success(make_uc, order_data):
    uc, order_svc, cart_svc, product_svc, session, session_maker = make_uc()
    order_id = "ord-123"

    order_svc.create_order.return_value = order_id
    order_svc.get_order_full_info.return_value = OrderFullInfoSchema(
        user_id=order_data.user_id,
        order_id=order_id,
        order_status=OrderStatus.created,
        delivery_method_name="Courier",
        client_name=order_data.client_name,
        client_number=order_data.client_number,
        client_address=order_data.client_address,
        items=[OrderItemSchema(product_name="A", quantity=1, unit_price=100)],
    )

    res = await uc(order_data)

    assert isinstance(res, OrderFullInfoSchema)
    assert res.order_id == order_id

    # open session transaction
    session_maker.assert_called_once()
    session.begin.assert_called_once()

    # Check that all services got the same session
    order_svc.create_order.assert_awaited_once_with(order_data, session)
    order_svc.insert_order_items_from_cart.assert_awaited_once_with(
        order_id=order_id, user_id=order_data.user_id, session=session
    )
    product_svc.decrease_product_stock_batch.assert_awaited_once_with(
        user_id=order_data.user_id, session=session
    )
    cart_svc.delete_all_user_carts.assert_awaited_once_with(
        user_id=order_data.user_id, session=session
    )
    order_svc.get_order_full_info.assert_awaited_once_with(
        order_id=order_id, session=session
    )


async def test_empty_cart_raises(make_uc, order_data):
    uc, order_svc, cart_svc, product_svc, session, session_maker = make_uc()

    order_svc.create_order.side_effect = EmptyUserCart(order_data.user_id)

    with pytest.raises(EmptyUserCart):
        await uc(order_data)

    session_maker.assert_called_once()
    session.begin.assert_called_once()

    order_svc.insert_order_items_from_cart.assert_not_called()
    product_svc.decrease_product_stock_batch.assert_not_called()
    cart_svc.delete_all_user_carts.assert_not_called()
    order_svc.get_order_full_info.assert_not_called()


async def test_out_of_stock_raises(make_uc, order_data):
    uc, order_svc, cart_svc, product_svc, session, session_maker = make_uc()

    order_svc.create_order.side_effect = OutOfStock(
        [{"product_name": "X", "need": 2, "stock": 1}]
    )

    with pytest.raises(OutOfStock):
        await uc(order_data)

    session_maker.assert_called_once()
    session.begin.assert_called_once()

    order_svc.insert_order_items_from_cart.assert_not_called()
    product_svc.decrease_product_stock_batch.assert_not_called()
    cart_svc.delete_all_user_carts.assert_not_called()
    order_svc.get_order_full_info.assert_not_called()
