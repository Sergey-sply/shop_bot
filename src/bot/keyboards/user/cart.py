from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from src.bot.callback.user.cart import CartIDCallbackFactory, CartPageCallbackFactory, \
    ChangeCartItemQuantityCallbackFactory, DeleteCartItemCallbackFactory, DeleteCartCallbackFactory
from src.bot.callback.user.order import CreateOrderCallbackFactory
from src.bot.keyboards.core import AbstractTelegramKeyboard
from src.application.schemas.cart import UserCartSchema, CartSchema


class UserCartListKeyboard(AbstractTelegramKeyboard):
    def __init__(self, cart: UserCartSchema, per_page: int = 5) -> None:
        self.cart = cart
        self.per_page = per_page

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:

        for item in self.cart.items:
            title = f"{item.name} | {item.quantity} | {item.unit_price} руб."
            callback = CartIDCallbackFactory(cart_id=item.cart_id).pack()
            button = InlineKeyboardButton(text=title, callback_data=callback)
            builder.row(button)

        navigation_buttons = []
        if self.cart.page > 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="<<",
                callback_data=CartPageCallbackFactory(page=self.cart.page - 1).pack()
            ))

        if self.cart.total_count > self.per_page:
            navigation_buttons.append(InlineKeyboardButton(
                text=(
                    f"{self.cart.page}/"
                    f"{self.cart.total_count // self.per_page + (1 if self.cart.total_count % self.per_page else 0)}"
                ),
                callback_data="#count#"
            ))

        if self.cart.page * self.per_page < self.cart.total_count:
            navigation_buttons.append(InlineKeyboardButton(
                text=">>",
                callback_data=CartPageCallbackFactory(page=self.cart.page + 1).pack()
            ))

        if navigation_buttons:
            builder.row(*navigation_buttons)

        if self.cart.items:
            delete_cart_items_btn = InlineKeyboardButton(
                text="Очистить корзину",
                callback_data=DeleteCartCallbackFactory().pack()
            )
            create_order_btn = InlineKeyboardButton(
                text="Оформить заказ",
                callback_data=CreateOrderCallbackFactory().pack()
            )
            builder.row(create_order_btn, delete_cart_items_btn)


class CartItemInfoKeyboard(AbstractTelegramKeyboard):
    def __init__(self, cart_item: CartSchema) -> None:
        self.cart = cart_item

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        quantity_btns = []

        quantity_btns.append(InlineKeyboardButton(
            text="+",
            callback_data=ChangeCartItemQuantityCallbackFactory(
                quantity=1,
                cart_id=self.cart.cart_id,
                prev_quantity=self.cart.quantity
            ).pack()
        ))

        if self.cart.quantity == 1:
            callback_data = DeleteCartItemCallbackFactory(
                cart_id=self.cart.cart_id,
            ).pack()
        else:
            callback_data = ChangeCartItemQuantityCallbackFactory(
                quantity=-1,
                cart_id=self.cart.cart_id,
                prev_quantity=self.cart.quantity
            ).pack()
        quantity_btns.append(InlineKeyboardButton(
            text="-",
            callback_data=callback_data
        ))

        builder.row(*quantity_btns)

        delete_kb = InlineKeyboardButton(
            text="удалить из корзины",
            callback_data=DeleteCartItemCallbackFactory(
                cart_id=self.cart.cart_id,
            ).pack()
        )

        builder.row(delete_kb)

        back_kb = InlineKeyboardButton(
            text="Вернуться",
            callback_data=CartPageCallbackFactory(
                page=1,
            ).pack()
        )

        builder.row(back_kb)


