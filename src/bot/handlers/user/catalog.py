from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dishka import FromDishka

from src.application.ports.services.cart import CartServicePort
from src.application.ports.services.category import CategoryServicePort
from src.application.ports.services.product import ProductServicePort
from src.bot.callback.catalog.category import CategoriesPageCallbackFactory, CategoryIDCallbackFactory
from src.bot.callback.catalog.product import ProductIDCallbackFactory, AddToCartCallbackFactory
from src.bot.handlers.builds.product import build_product_view
from src.bot.const import BASE_PER_PAGE
from src.bot.keyboards.catalog.catalog_menu import CategoryListKeyboard
from src.bot.keyboards.catalog.product import ProductCategoryListKeyboard, ProductKeyboard
from src.bot.keyboards.factory import combine_keyboards
from src.bot.utils.message_processor import get_media_obj
from src.config.settings import product_image_path, default_product_image_path

catalog_router = Router()

@catalog_router.message(F.text == "Товары")
async def get_categories_hnd(message: Message, state: FSMContext, ctg_service: FromDishka[CategoryServicePort]):
    await state.clear()
    categories = await ctg_service.get_category_list(page=1, per_page=BASE_PER_PAGE)

    if categories is None:
        await message.answer(
            text="Товаров нет."
        )
        return

    keyboard_rules = [CategoryListKeyboard(categories)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await message.answer(
        text="Выберите категорию",
        reply_markup=keyboard
    )


@catalog_router.callback_query(CategoriesPageCallbackFactory.filter())
async def get_categories_clb(
    callback: CallbackQuery,
    callback_data: CategoriesPageCallbackFactory,
    ctg_service: FromDishka[CategoryServicePort]
):
    categories = await ctg_service.get_category_list(page=callback_data.page, per_page=BASE_PER_PAGE)
    if categories is None:
        await callback.answer(
            text="Категорий нет"
        )
        return

    keyboard_rules = [CategoryListKeyboard(categories)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await callback.message.edit_text(
        text="Выберите категорию",
        reply_markup=keyboard
    )


@catalog_router.callback_query(CategoryIDCallbackFactory.filter())
async def get_products_from_category_hnd(
    callback: CallbackQuery,
    callback_data: CategoryIDCallbackFactory,
    bot: Bot,
    product_service: FromDishka[ProductServicePort]
):
    products = await product_service.get_product_list_by_category_id(
        category_id=callback_data.category_id,
        page=callback_data.page,
        per_page=BASE_PER_PAGE
    )
    if products is None:
        await callback.answer(
            text="Товаров в выбранной категории нет"
        )
        return
    keyboard_rules = [ProductCategoryListKeyboard(products)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    msg = "Выберите товар"
    if callback.message.caption:
        await callback.message.delete()
        await bot.send_message(
            text=msg,
            reply_markup=keyboard,
            chat_id=callback.message.chat.id
        )
    else:
        await callback.message.edit_text(
            text=msg,
            reply_markup=keyboard
        )


@catalog_router.callback_query(ProductIDCallbackFactory.filter())
async def get_product_info_hnd(
    callback: CallbackQuery,
    callback_data: ProductIDCallbackFactory,
    product_service: FromDishka[ProductServicePort]
):
    product_info = await product_service.get_product_info(product_id=callback_data.product_id)

    keyboard_rules = [ProductKeyboard(product_info)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    msg = build_product_view(product_info)

    if product_info.image:
        image_path = product_image_path + product_info.image
    else:
        image_path = default_product_image_path
    image = await get_media_obj(image_path=image_path, caption=msg)

    await callback.message.edit_media(
        media=image,
        reply_markup=keyboard
    )


@catalog_router.callback_query(AddToCartCallbackFactory.filter())
async def add_to_cart_hnd(
    callback: CallbackQuery,
    callback_data: AddToCartCallbackFactory,
    cart_service: FromDishka[CartServicePort]
):

    cart_id = await cart_service.create_cart(
        user_id=callback.message.chat.id,
        product_id=callback_data.product_id,
        quantity=1
    )
    if cart_id is None:
        await callback.answer("Товар уже в корзине!")
        return

    await callback.answer("Товар успешно добавлен в корзину")


