from aiogram.filters.callback_data import CallbackData

from src.bot.callback.base import BasePageCallback

class CartPageCallbackFactory(BasePageCallback, prefix="cart_page"): ...

class CartIDCallbackFactory(CallbackData, prefix="cartID"):
    cart_id: int

class ChangeCartItemQuantityCallbackFactory(CallbackData, prefix="chng_q_cart"):
    cart_id: int
    quantity: int
    prev_quantity: int

class DeleteCartItemCallbackFactory(CallbackData, prefix="delete_cart_item"):
    cart_id: int


class DeleteCartCallbackFactory(CallbackData, prefix="delete_cart"): ...