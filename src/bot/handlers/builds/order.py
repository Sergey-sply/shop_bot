from src.bot.handlers.prompts import ORDER_STATUS_PROMPTS
from src.application.schemas.order import OrderFullInfoSchema


def build_order_view(
    order_info: OrderFullInfoSchema
) -> str:
    total_amount = sum(item.quantity * item.unit_price for item in order_info.items)

    status = ORDER_STATUS_PROMPTS.get(order_info.order_status.value)
    msg = (
        f"Номер заказа: {order_info.order_id}\n\n"
        f"Способ доставки: {order_info.delivery_method_name}\n"
        f"ФИО: {order_info.client_name}\n"
        f"Номер телефона: {order_info.client_number}\n"
        f"Адрес: {order_info.client_address}\n\n"
        f"Статус заказа: {status}\n"
        f"Итоговая стоимость: {total_amount} руб."
    )

    return msg

