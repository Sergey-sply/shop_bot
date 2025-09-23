from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder

from src.bot.callback.catalog.category import CategoriesPageCallbackFactory, CategoryIDCallbackFactory
from src.bot.callback.catalog.product import ProductIDCallbackFactory, \
    AddToCartCallbackFactory

from src.bot.keyboards.core import AbstractTelegramKeyboard

from src.application.schemas.product import CategoryProductsListSchema, ProductFullInfo


class ProductCategoryListKeyboard(AbstractTelegramKeyboard):
    def __init__(self, products: CategoryProductsListSchema, per_page: int = 5) -> None:
        self.products = products
        self.per_page = per_page

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        for product in self.products.products:
            title = f"{product.name}"
            callback = ProductIDCallbackFactory(product_id=product.id).pack()
            button = InlineKeyboardButton(text=title, callback_data=callback)
            builder.row(button)

        navigation_buttons = []
        if self.products.page > 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="<<",
                callback_data=CategoryIDCallbackFactory(
                    page=self.products.page - 1,
                    category_id=self.products.category_id
                ).pack()
            ))

        if self.products.total_count > self.per_page:
            navigation_buttons.append(InlineKeyboardButton(
                text=f"{self.products.page}/"
                     f"{self.products.total_count // self.per_page + (1 if self.products.total_count % self.per_page else 0)}",
                callback_data="#count#"
            ))

        if self.products.page * self.per_page < self.products.total_count:
            navigation_buttons.append(InlineKeyboardButton(
                text=">>",
                callback_data=CategoryIDCallbackFactory(
                    page=self.products.page + 1,
                    category_id=self.products.category_id
                ).pack()
            ))

        if navigation_buttons:
            builder.row(*navigation_buttons)

        back_kb = InlineKeyboardButton(
            text="Вернуться",
            callback_data=CategoriesPageCallbackFactory(
                page=1,
            ).pack()
        )

        builder.row(back_kb)


class ProductKeyboard(AbstractTelegramKeyboard):
    def __init__(self, product_info: ProductFullInfo) -> None:
        self.product_info = product_info

    def generate_keyboard(
            self,
            builder: InlineKeyboardBuilder | ReplyKeyboardBuilder, *args, **kwargs
    ) -> None:
        builder.add(
            InlineKeyboardButton(
                text="Добавить в корзину",
                callback_data=AddToCartCallbackFactory(product_id=self.product_info.id).pack()
            )
        )

        builder.add(
            InlineKeyboardButton(
                text="Вернуться",
                callback_data=CategoryIDCallbackFactory(
                    category_id=self.product_info.category_id,
                    page=1
                ).pack()
            )
        )