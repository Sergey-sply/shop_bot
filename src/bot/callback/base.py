from typing import TypeVar

from aiogram.filters.callback_data import CallbackData


class BasePageCallback(CallbackData, prefix="page"):
    page: int
