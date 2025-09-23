from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.callback.admin.order import AdmOrderIDCallbackFactory, AdmOrderListCallbackFactory, \
    AdmOrderUpdateStatusCallbackFactory, AdmOrderStatusCallbackFactory, AdmOrderCancelUpdateStatusCallbackFactory, \
    AdmStartCallbackFactory
from src.bot.keyboards.core import AbstractTelegramKeyboard
from src.application.schemas.order import OrderListSchema


class AdminOrderListKeyboard(AbstractTelegramKeyboard):
    def __init__(self, orders: OrderListSchema, per_page: int = 5) -> None:
        self.orders = orders
        self.per_page = per_page

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        for order_id in self.orders.orders:
            title = f"{order_id}"
            callback = AdmOrderIDCallbackFactory(order_id=order_id).pack()
            button = InlineKeyboardButton(text=title, callback_data=callback)
            builder.row(button)

        navigation_buttons = []
        if self.orders.page > 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="<<",
                callback_data=AdmOrderListCallbackFactory(page=self.orders.page - 1).pack()
            ))

        if self.orders.total_count > self.per_page:
            navigation_buttons.append(InlineKeyboardButton(
                text=f"{self.orders.page}/"
                     f"{self.orders.total_count // self.per_page + (1 if self.orders.total_count % self.per_page else 0)}",
                callback_data="#count#"
            ))

        if self.orders.page * self.per_page < self.orders.total_count:
            navigation_buttons.append(InlineKeyboardButton(
                text=">>",
                callback_data=AdmOrderListCallbackFactory(page=self.orders.page + 1).pack()
            ))

        if navigation_buttons:
            builder.row(*navigation_buttons)

        builder.row(
            InlineKeyboardButton(
                text="Вернуться",
                callback_data=AdmStartCallbackFactory().pack()
            )
        )



class AdminOrderInfoKeyboard(AbstractTelegramKeyboard):
    def __init__(self, order_id: str, actual_status: str) -> None:
        self.order_id = order_id
        self.actual_status = actual_status

    def generate_keyboard(
            self,
            builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        builder.row(
            InlineKeyboardButton(
                text="Изменить статус",
                callback_data=AdmOrderUpdateStatusCallbackFactory(
                    order_id=self.order_id,
                    actual_status=self.actual_status
                ).pack()
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="Вернуться",
                callback_data=AdmOrderListCallbackFactory(
                    page=1
                ).pack()
            )
        )

class AdminOrderStatusKeyboard(AbstractTelegramKeyboard):
    def __init__(self, statuses: dict[str, str], order_id: str) -> None:
        self.statuses = statuses
        self.order_id = order_id

    def generate_keyboard(
            self,
            builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        for status in self.statuses:
            title = f"{status}"
            callback = AdmOrderStatusCallbackFactory(order_id=self.order_id, status=status).pack()
            button = InlineKeyboardButton(text=title, callback_data=callback)
            builder.row(button)

        builder.row(
            InlineKeyboardButton(
                text="Отмена",
                callback_data=AdmOrderCancelUpdateStatusCallbackFactory(order_id=self.order_id).pack()
            )
        )
