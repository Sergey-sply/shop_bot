from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.callback.admin.order import AdmOrderListCallbackFactory, AdmStartCallbackFactory
from src.bot.callback.admin.product import AdmProductListCallbackFactory, \
    AdmProductIDCallbackFactory, AdmChangeProductCallbackFactory, AdmCreateProductCallbackFactory, \
    CreateProductCategoryCallbackFactory, AdmCreateProductConfirmCallbackFactory, AdmChangeProductImgCallbackFactory
from src.bot.keyboards.core import AbstractTelegramKeyboard
from src.application.schemas.category import CategoryListSchema
from src.application.schemas.product import ProductListSchema


class AdminPanelKeyboard(AbstractTelegramKeyboard):

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        builder.add(
            InlineKeyboardButton(
                text="Товары",
                callback_data=AdmProductListCallbackFactory(page=1).pack()
            )
        )

        builder.add(
            InlineKeyboardButton(
                text="Заказы",
                callback_data=AdmOrderListCallbackFactory(page=1).pack()
            )
        )


class AdminProductsListKeyboard(AbstractTelegramKeyboard):
    def __init__(self, products: ProductListSchema, per_page: int = 5) -> None:
        self.products = products
        self.per_page = per_page

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        if self.products:
            for product in self.products.products:
                title = f"{product.name} | {product.quantity} | {product.price} руб."
                callback = AdmProductIDCallbackFactory(product_id=product.id).pack()
                button = InlineKeyboardButton(text=title, callback_data=callback)
                builder.row(button)

            navigation_buttons = []
            if self.products.page > 1:
                navigation_buttons.append(InlineKeyboardButton(
                    text="<<",
                    callback_data=AdmProductListCallbackFactory(page=self.products.page - 1).pack()
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
                    callback_data=AdmProductListCallbackFactory(page=self.products.page + 1).pack()
                ))

            if navigation_buttons:
                builder.row(*navigation_buttons)


        builder.row(
            InlineKeyboardButton(
                text="Добавить товар",
                callback_data=AdmCreateProductCallbackFactory(page=1).pack()
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="Вернуться",
                callback_data=AdmStartCallbackFactory().pack()
            )
        )


class AdminProductSettingsKeyboard(AbstractTelegramKeyboard):
    def __init__(self,product_id: int) -> None:
        self.product_id = product_id

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        kb_rows = [
            ["Изменить описание", "description"],
            ["Изменить название", "name"],
            ["Изменить цену", "price"],
        ]
        for text, field in kb_rows:
            builder.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=AdmChangeProductCallbackFactory(field=field, product_id=self.product_id).pack()
                )
            )
        builder.add(
            InlineKeyboardButton(
                text="Изменить изображение",
                callback_data=AdmChangeProductImgCallbackFactory(product_id=self.product_id).pack()
            )
        )
        builder.adjust(2, )
        builder.row(
            InlineKeyboardButton(
                text="Вернуться",
                callback_data=AdmProductListCallbackFactory(page=1).pack()
            )
        )


class AdminCreateProductKeyboard(AbstractTelegramKeyboard):
    def __init__(self, categories: CategoryListSchema, per_page: int = 5) -> None:
        self.categories = categories
        self.per_page = per_page

    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        for category in self.categories.categories:
            title = f"{category.name}"
            callback = CreateProductCategoryCallbackFactory(
                category_id=category.id,
                category_name=category.name
            ).pack()
            button = InlineKeyboardButton(text=title, callback_data=callback)
            builder.row(button)

        navigation_buttons = []
        if self.categories.page > 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="<<",
                callback_data=AdmCreateProductCallbackFactory(page=self.categories.page - 1).pack()
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
                callback_data=AdmCreateProductCallbackFactory(page=self.categories.page + 1).pack()
            ))

        if navigation_buttons:
            builder.row(*navigation_buttons)


class AdminConfirmCreateProductKeyboard(AbstractTelegramKeyboard):
    def generate_keyboard(
        self,
        builder: InlineKeyboardBuilder, *args, **kwargs
    ) -> None:
        builder.add(
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=AdmCreateProductConfirmCallbackFactory(confirm=True).pack()
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="Отмена",
                callback_data=AdmCreateProductConfirmCallbackFactory(confirm=False).pack()
            )
        )