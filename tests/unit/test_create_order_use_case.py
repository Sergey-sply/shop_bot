import pytest

from src.application.ports.services.cart import CartServicePort
from src.application.ports.services.order import OrderServicePort
from src.application.ports.services.product import ProductServicePort
from src.application.use_cases.order.create import CreateOrderUseCase
from src.core.enums.order import OrderStatus
from src.core.exceptions.order import OutOfStock, EmptyUserCart
from src.application.schemas.order import OrderSchemaCreate, OrderFullInfoSchema, OrderItemSchema

pytestmark = pytest.mark.asyncio


@pytest.fixture
def session():
    return object()


@pytest.fixture
def order_data() -> OrderSchemaCreate:
    return OrderSchemaCreate(
        user_id=7, delivery_method_id=2,
        client_name="Ivan", client_number="+123", client_address="Earth"
    )


@pytest.fixture
def make_uc(mocker):
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

        uc = CreateOrderUseCase(order_svc, cart_svc, product_svc)
        return uc, order_svc, cart_svc, product_svc
    return _


async def test_success(make_uc, order_data, session):
    uc, order_svc, cart_svc, product_svc = make_uc()
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

    res = await uc(order_data, session=session)

    assert isinstance(res, OrderFullInfoSchema)
    assert res.order_id == order_id

    order_svc.create_order.assert_awaited_once_with(order_data, session)
    order_svc.insert_order_items_from_cart.assert_awaited_once()
    product_svc.decrease_product_stock_batch.assert_awaited_once()
    cart_svc.delete_all_user_carts.assert_awaited_once()
    order_svc.get_order_full_info.assert_awaited_once()


async def test_empty_cart_raises(make_uc, order_data, session):
    uc, order_svc, cart_svc, product_svc = make_uc()

    order_svc.create_order.side_effect = EmptyUserCart(order_data.user_id)

    with pytest.raises(EmptyUserCart):
        await uc(order_data, session=session)

    order_svc.insert_order_items_from_cart.assert_not_called()
    product_svc.decrease_product_stock_batch.assert_not_called()
    cart_svc.delete_all_user_carts.assert_not_called()
    order_svc.get_order_full_info.assert_not_called()


async def test_out_of_stock_raises(make_uc, order_data, session):
    uc, order_svc, cart_svc, product_svc = make_uc()

    order_svc.create_order.side_effect = OutOfStock(
        [{"product_name": "X", "need": 2, "stock": 1}]
    )

    with pytest.raises(OutOfStock):
        await uc(order_data, session=session)

    order_svc.insert_order_items_from_cart.assert_not_called()
    product_svc.decrease_product_stock_batch.assert_not_called()
    cart_svc.delete_all_user_carts.assert_not_called()
    order_svc.get_order_full_info.assert_not_called()
