from aiogram.filters.callback_data import CallbackData

from src.bot.callback.base import BasePageCallback


class ProductIDCallbackFactory(CallbackData, prefix="productID"):
    product_id: int


class ProductsPageCallbackFactory(BasePageCallback, prefix="prod_page"):
    category_id: int

class AddToCartCallbackFactory(CallbackData, prefix="add_cart"):
    product_id: int