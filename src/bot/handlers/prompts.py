from src.core.enums.order import OrderStatus

PRODUCT_FIELD_PROMPTS: dict[str, str] = {
    "name": "Введите новое название (1–32 символов). Напишите «отмена» для выхода.",
    "description": "Введите новое описание (1–128 символов). Напишите «отмена» для выхода.",
    "price": "Введите новую цену (целое число, больше 0). Напишите «отмена» для выхода.",
}

ORDER_STATUS_PROMPTS: dict[str, str] = {
    OrderStatus.created.value: "Создан",
    OrderStatus.paid.value: "Оплачен",
    OrderStatus.delivered.value: "Доставлен",
}