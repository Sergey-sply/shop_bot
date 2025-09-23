from aiogram.filters.callback_data import CallbackData

from src.bot.callback.base import BasePageCallback


class CategoryIDCallbackFactory(CallbackData, prefix="categoryID"):
    category_id: int
    page: int = 1


class CategoriesPageCallbackFactory(BasePageCallback, prefix="cat_page"): ...
