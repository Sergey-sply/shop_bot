from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.factory import combine_keyboards
from src.bot.keyboards.user.cart import UserCartListKeyboard, CartItemInfoKeyboard
from src.application.schemas.cart import CartSchema, UserCartSchema


async def build_cart_list_view(
    carts: UserCartSchema | None
) -> tuple[str, InlineKeyboardMarkup | None]:

    if not carts:
        return "Ваша корзина пуста.", None


    msg = (
        "Ваша корзина\n\n"
        f"Общая стоимость: {carts.total_amount} руб."
    )

    keyboard_rules = [UserCartListKeyboard(carts)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    return msg, keyboard


def build_cart_info_view(
    cart_info:  CartSchema,
)-> tuple[str, InlineKeyboardMarkup]:
    msg = (
        f"Товар: {cart_info.name}\n"
        f"Цена: {cart_info.unit_price} руб.\n\n"
        f"Количество: {cart_info.quantity}\n"
        f"Итоговая стоимость: {cart_info.quantity * cart_info.unit_price} руб."
    )

    keyboard_rules = [CartItemInfoKeyboard(cart_info)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    return msg, keyboard
