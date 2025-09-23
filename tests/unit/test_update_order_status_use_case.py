import pytest

from src.application.ports.services.order import OrderServicePort
from src.application.use_cases.order.update import UpdateOrderStatusUseCase
from src.core.enums.order import OrderStatus
from src.application.schemas.order import OrderFullInfoSchema, OrderItemSchema


pytestmark = pytest.mark.asyncio


@pytest.fixture
def session():
    return object()


@pytest.fixture
def make_uc(mocker):
    def _():
        order_svc: OrderServicePort = mocker.create_autospec(
            OrderServicePort, instance=True, spec_set=True
        )
        uc = UpdateOrderStatusUseCase(order_svc)
        return uc, order_svc
    return _


async def test_update_status_happy_path(make_uc, session):
    uc, order_svc = make_uc()

    order_id = "ord-42"
    new_status = OrderStatus.paid

    order_svc.get_order_full_info.return_value = OrderFullInfoSchema(
        user_id=7,
        order_id=order_id,
        order_status=new_status,
        delivery_method_name="Courier",
        client_name="Ivan",
        client_number="+123",
        client_address="Earth",
        items=[OrderItemSchema(product_name="A", quantity=1, unit_price=100)],
    )

    res = await uc(order_id=order_id, status=new_status, session=session)

    assert isinstance(res, OrderFullInfoSchema)
    assert res.order_id == order_id
    assert res.order_status == new_status

    order_svc.change_order_status.assert_awaited_once_with(
        order_id=order_id, status=new_status, session=session
    )
    order_svc.get_order_full_info.assert_awaited_once_with(
        order_id=order_id, session=session
    )


async def test_update_status_propagates_error_and_stops(make_uc, session):
    uc, order_svc = make_uc()

    order_id = "ord-42"
    new_status = OrderStatus.paid

    order_svc.change_order_status.side_effect = RuntimeError("db down")

    with pytest.raises(RuntimeError):
        await uc(order_id=order_id, status=new_status, session=session)

    order_svc.get_order_full_info.assert_not_called()
