from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from src.bot.callback.catalog.category import CategoryIDCallbackFactory, CategoriesPageCallbackFactory
from src.bot.keyboards.core import AbstractTelegramKeyboard
from src.application.schemas.category import CategoryListSchema


class CategoryListKeyboard(AbstractTelegramKeyboard):
    def __init__(self, categories: CategoryListSchema, per_page: int = 5) -> None:
        self.categories = categories
        self.per_page = per_page

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        for category in self.categories.categories:
            title = f"{category.name}"
            callback = CategoryIDCallbackFactory(category_id=category.id).pack()
            button = InlineKeyboardButton(text=title, callback_data=callback)
            builder.row(button)

        navigation_buttons = []
        if self.categories.page > 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="<<",
                callback_data=CategoriesPageCallbackFactory(page=self.categories.page - 1).pack()
            ))

        if self.categories.total_count > self.per_page:
            navigation_buttons.append(InlineKeyboardButton(
                text=f"{self.categories.page}/"
                     f"{self.categories.total_count // self.per_page + (1 if self.categories.total_count % self.per_page else 0)}",
                callback_data="#count#"
            ))

        if self.categories.page * self.per_page < self.categories.total_count:
            navigation_buttons.append(InlineKeyboardButton(
                text=">>",
                callback_data=CategoriesPageCallbackFactory(page=self.categories.page + 1).pack()
            ))

        if navigation_buttons:
            builder.row(*navigation_buttons)

