import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.ports.services.order import OrderServicePort
from src.application.use_cases.order.update import UpdateOrderStatusUseCase
from src.core.enums.order import OrderStatus
from src.application.schemas.order import OrderFullInfoSchema, OrderItemSchema

pytestmark = pytest.mark.asyncio


@pytest.fixture
def make_uc(mocker):
    """
    Generating mock services, uc, async session
    """
    def _():
        order_svc: OrderServicePort = mocker.create_autospec(
            OrderServicePort, instance=True, spec_set=True
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

        uc = UpdateOrderStatusUseCase(order_svc, session_maker)
        return uc, order_svc, session, session_maker
    return _


async def test_update_status_happy_path(make_uc):
    uc, order_svc, session, session_maker = make_uc()

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

    res = await uc(order_id=order_id, status=new_status)

    assert isinstance(res, OrderFullInfoSchema)
    assert res.order_id == order_id
    assert res.order_status == new_status

    # open session transaction
    session_maker.assert_called_once()
    session.begin.assert_called_once()

    # Check that all services got the same session
    order_svc.change_order_status.assert_awaited_once_with(
        order_id=order_id, status=new_status, session=session
    )
    order_svc.get_order_full_info.assert_awaited_once_with(
        order_id=order_id, session=session
    )


async def test_update_status_propagates_error_and_stops(make_uc):
    uc, order_svc, session, session_maker = make_uc()

    order_id = "ord-42"
    new_status = OrderStatus.paid

    order_svc.change_order_status.side_effect = RuntimeError("db down")

    with pytest.raises(RuntimeError):
        await uc(order_id=order_id, status=new_status)

    session_maker.assert_called_once()
    session.begin.assert_called_once()

    order_svc.get_order_full_info.assert_not_called()
