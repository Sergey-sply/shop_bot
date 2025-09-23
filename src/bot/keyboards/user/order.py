from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder

from src.bot.callback.user.order import OrderDMIDCallbackFactory, ConfirmOrderCallbackFactory, \
    OrderIDCallbackFactory, OrderListCallbackFactory
from src.bot.keyboards.core import AbstractTelegramKeyboard
from src.application.schemas.delivery import DeliveryMethodSchema


class DeliveryMethodsListKeyboard(AbstractTelegramKeyboard):
    def __init__(self, delivery_list: list[DeliveryMethodSchema]) -> None:
        self.delivery_list = delivery_list

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:

        for item in self.delivery_list:
            title = f"{item.name}"
            callback = OrderDMIDCallbackFactory(
                delivery_method_id=item.id,
                delivery_method_name=item.name
            ).pack()
            button = InlineKeyboardButton(text=title, callback_data=callback)
            builder.row(button)


class ConfirmOrderKeyboard(AbstractTelegramKeyboard):

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        builder.add(
            InlineKeyboardButton(
                text="Подтвердить заказ",
                callback_data=ConfirmOrderCallbackFactory(confirm=True).pack()
            )
        )

        builder.add(
            InlineKeyboardButton(
                text="Отменить заказ",
                callback_data=ConfirmOrderCallbackFactory(confirm=False).pack()
            )
        )


class UserOrdersListKeyboard(AbstractTelegramKeyboard):
    def __init__(self, order_ids: list[str]) -> None:
        self.order_ids = order_ids

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:

        for order_id in self.order_ids:
            title = f"{order_id}"
            callback = OrderIDCallbackFactory(order_id=order_id).pack()
            button = InlineKeyboardButton(text=title, callback_data=callback)
            builder.row(button)


class OrderInfoKeyboard(AbstractTelegramKeyboard):

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder | ReplyKeyboardBuilder, *args, **kwargs
    ) -> None:
        builder.add(
            InlineKeyboardButton(
                text="Вернуться",
                callback_data=OrderListCallbackFactory().pack()
            )
        )


