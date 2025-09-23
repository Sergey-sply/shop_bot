import os

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from pydantic import ValidationError

from src.application.ports.services.category import CategoryServicePort
from src.application.ports.services.product import ProductServicePort
from src.bot.callback.admin.product import AdmProductListCallbackFactory, AdmProductIDCallbackFactory, \
    AdmChangeProductCallbackFactory, AdmCreateProductCallbackFactory, CreateProductCategoryCallbackFactory, \
    AdmCreateProductConfirmCallbackFactory, AdmChangeProductImgCallbackFactory
from src.bot.filters.role import RoleFilter
from src.bot.handlers.builds.product import build_product_view
from src.bot.handlers.prompts import PRODUCT_FIELD_PROMPTS
from src.bot.keyboards.admin.product import AdminProductsListKeyboard, AdminProductSettingsKeyboard, \
    AdminCreateProductKeyboard, AdminConfirmCreateProductKeyboard
from src.bot.keyboards.factory import combine_keyboards
from src.bot.states.product import UpdateProductState, CreateProductState, ChangeImageProductState
from src.bot.utils.message_processor import get_media_obj
from src.config.settings import product_image_path, default_product_image_path
from src.bot.const import BASE_PER_PAGE
from src.infrastructure.logging.config import get_logger
from src.application.schemas.product import ProductUpdate, ProductSchemaCreate

log = get_logger(__name__)


admin_product_router = Router()
admin_product_router.message.filter(RoleFilter(required_role="admin"))


@admin_product_router.callback_query(AdmProductListCallbackFactory.filter())
async def product_list_adm_hnd(
    callback: CallbackQuery,
    callback_data: AdmProductListCallbackFactory,
    product_service: FromDishka[ProductServicePort]
):

    products = await product_service.get_product_list(
        page=callback_data.page,
        per_page=BASE_PER_PAGE
    )

    msg = "Товары"

    keyboard_rules = [AdminProductsListKeyboard(products)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            text=msg,
            reply_markup=keyboard
        )
        return
    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )


@admin_product_router.callback_query(AdmProductIDCallbackFactory.filter())
async def product_settings_hnd(
    callback: CallbackQuery,
    callback_data: AdmProductIDCallbackFactory,
    product_service: FromDishka[ProductServicePort]
):
    product_info = await product_service.get_product_info(
        product_id=callback_data.product_id
    )

    keyboard_rules = [AdminProductSettingsKeyboard(product_info.id)]
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



@admin_product_router.callback_query(AdmChangeProductCallbackFactory.filter())
async def update_product_field_hnd(
    callback: CallbackQuery,
    callback_data: AdmChangeProductCallbackFactory,
    state: FSMContext
):
    field = callback_data.field
    product_id = callback_data.product_id
    message_id = callback.message.message_id
    await state.update_data(field=field, product_id=product_id, message_id=message_id)

    await callback.message.edit_caption(caption=PRODUCT_FIELD_PROMPTS.get(field))
    await state.set_state(UpdateProductState.wait_value)


@admin_product_router.message(UpdateProductState.wait_value)
async def update_product_wait_value_hnd(
    message: Message,
    state: FSMContext,
    bot: Bot,
    product_service: FromDishka[ProductServicePort]
):
    text = message.text

    if text.lower() == "отмена":
        await state.clear()
        await message.answer("Отмена")
        return

    data = await state.get_data()
    field = data.get("field")
    product_id = data.get("product_id")
    message_id = data.get("message_id")

    try:
        product_new_data = ProductUpdate.validate_python(
            {
                "field": field,
                "value": text
            }
        )

    except ValidationError as e:
        error = e.errors()[0]
        msg = error.get("msg", "Некорректное значение")
        print(msg)
        await message.answer(f"Некорректное значение")
        return

    updated_product = await product_service.update_product(product_id=product_id, data=product_new_data)
    if not updated_product:
        await message.answer("Товар не найден или не обновлён")
        await state.clear()
        return


    await state.clear()
    await message.delete()
    msg = build_product_view(updated_product)

    keyboard_rules = [AdminProductSettingsKeyboard(updated_product.id)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())
    
    await bot.edit_message_caption(
        caption=msg,
        reply_markup=keyboard,
        chat_id=message.from_user.id,
        message_id=message_id
    )


@admin_product_router.callback_query(AdmChangeProductImgCallbackFactory.filter())
async def update_product_img_adm_hnd(
    callback: CallbackQuery,
    callback_data: AdmChangeProductImgCallbackFactory,
    state: FSMContext
):
    await state.update_data(
        product_id=callback_data.product_id,
        message_id=callback.message.message_id
    )
    await callback.message.edit_caption(
        caption="Отправьте изображение в чат или напишите 'отмена'"
    )
    await state.set_state(ChangeImageProductState.image)


@admin_product_router.message(ChangeImageProductState.image)
async def update_product_wait_img_adm_hnd(
    message: Message,
    state: FSMContext,
    bot: Bot,
    product_service: FromDishka[ProductServicePort]
):
    data = await state.get_data()
    product_id = data.get("product_id")
    message_id = data.get("message_id")

    if not message.photo:
        if message.text.lower() == "отмена":
            product_info = await product_service.get_product_info(
                product_id=product_id
            )
            await state.clear()
            await message.delete()
            msg = build_product_view(product_info)

            keyboard_rules = [AdminProductSettingsKeyboard(product_info.id)]
            keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

            await bot.edit_message_caption(
                caption=msg,
                reply_markup=keyboard,
                chat_id=message.from_user.id,
                message_id=message_id
            )
            return
        await message.delete()
        return

    image = message.photo[-1]

    filename = f"product_set_{product_id}.jpg"
    image_path = os.path.join(product_image_path, filename)

    await message.bot.download(file=image, destination=image_path)

    product_new_data = ProductUpdate.validate_python(
        {
            "field": "image",
            "value": filename
        }
    )
    updated_product = await product_service.update_product(product_id=product_id, data=product_new_data)
    if not updated_product:
        await message.answer("Товар не найден или не обновлён")
        await state.clear()
        return

    await state.clear()
    await message.delete()
    msg = build_product_view(updated_product)

    keyboard_rules = [AdminProductSettingsKeyboard(updated_product.id)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    if updated_product.image:
        image_path = product_image_path + updated_product.image
    else:
        image_path = default_product_image_path
    image = await get_media_obj(image_path=image_path, caption=msg)

    await bot.edit_message_media(
        media=image,
        reply_markup=keyboard,
        chat_id=message.from_user.id,
        message_id=message_id
    )


@admin_product_router.callback_query(AdmCreateProductCallbackFactory.filter())
async def create_product_adm_hnd(
    callback: CallbackQuery,
    state: FSMContext,
    category_service: FromDishka[CategoryServicePort]
):
    categories = await category_service.get_category_list(
        per_page=BASE_PER_PAGE,
        page=1
    )

    if categories is None:
        await callback.answer("Сначала нужно создать категории")
        return

    keyboard_rules = [AdminCreateProductKeyboard(categories)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await callback.message.edit_text(
        text="Выберите категорию товара",
        reply_markup=keyboard
    )
    await state.set_state(CreateProductState.category)


@admin_product_router.callback_query(CreateProductState.category, CreateProductCategoryCallbackFactory.filter())
async def create_product_wait_category_hnd(
    callback: CallbackQuery,
    callback_data: CreateProductCategoryCallbackFactory,
    state: FSMContext,
):
    category_id = callback_data.category_id
    category_name = callback_data.category_name
    message_id = callback.message.message_id

    await state.update_data(
        category_id=category_id,
        category_name=category_name,
        message_id=message_id
    )

    msg = f"Категория: {category_name}\n"
    msg += "Укажите название (от 1 до 32 символов)\n"

    await callback.message.edit_text(
        text=msg,
        reply_markup=None
    )

    await state.set_state(CreateProductState.name)


@admin_product_router.message(CreateProductState.name)
async def create_product_wait_name_hnd(
    message: Message,
    state: FSMContext,
    bot: Bot
):

    name = message.text
    chat_id = message.from_user.id

    await message.delete()
    data = await state.get_data()

    category_name = data.get("category_name")
    message_id = data.get("message_id")

    msg = (
        f"Категория: {category_name}\n"
    )

    if len(name) > 32:
        msg += "\nДлина названия должна быть не более 32 символов!"
        await bot.edit_message_text(
            text=msg,
            message_id=message_id,
            chat_id=chat_id
        )
        return

    await state.update_data(name=name)

    msg += (
        f"Название: {name}\n\n"
        "Укажите описание (от 1 до 128 символов)"
    )

    await bot.edit_message_text(
        text=msg,
        message_id=message_id,
        chat_id=chat_id
    )

    await state.set_state(CreateProductState.description)


@admin_product_router.message(CreateProductState.description)
async def create_product_wait_desc_hnd(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    description = message.text
    chat_id = message.from_user.id

    await message.delete()
    data = await state.get_data()

    category_name = data.get("category_name")
    name = data.get("name")
    message_id = data.get("message_id")

    msg = (
        f"Категория: {category_name}\n"
        f"Название: {name}\n"
    )

    if len(description) > 128:
        msg += "\nДлина описание должна быть не более 128 символов!"
        await bot.edit_message_text(
            text=msg,
            message_id=message_id,
            chat_id=chat_id
        )
        return

    await state.update_data(description=description)

    msg += (
        f"Описание: {description}\n\n"
        "Укажите цену (целое, больше 0)"
    )

    await bot.edit_message_text(
        text=msg,
        message_id=message_id,
        chat_id=chat_id
    )

    await state.set_state(CreateProductState.price)


@admin_product_router.message(CreateProductState.price)
async def create_product_wait_price_hnd(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    text = message.text
    chat_id = message.from_user.id

    await message.delete()
    data = await state.get_data()

    category_name = data.get("category_name")
    name = data.get("name")
    description = data.get("description")
    message_id = data.get("message_id")

    msg = (
        f"Категория: {category_name}\n"
        f"Название: {name}\n"
        f"Описание: {description}\n"
    )

    try:
        price = int(text)
        if price <= 0 :
            msg += "\nЦена должна быть целым числом больше 0"
            try:
                await bot.edit_message_text(
                    text=msg,
                    message_id=message_id,
                    chat_id=chat_id
                )
            except Exception: pass
            return
    except ValueError:
        msg += "\nЦена должна быть целым числом больше 0"
        try:
            await bot.edit_message_text(
                text=msg,
                message_id=message_id,
                chat_id=chat_id
            )
        except Exception: pass

        return

    await state.update_data(price=price)

    msg += (
        f"Цена: {price} руб.\n\n"
        "Укажите количество"
    )

    await bot.edit_message_text(
        text=msg,
        message_id=message_id,
        chat_id=chat_id
    )

    await state.set_state(CreateProductState.quantity)


@admin_product_router.message(CreateProductState.quantity)
async def create_product_wait_quantity_hnd(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    text = message.text
    chat_id = message.from_user.id

    await message.delete()
    data = await state.get_data()

    category_name = data.get("category_name")
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    message_id = data.get("message_id")

    msg = (
        f"Категория: {category_name}\n"
        f"Название: {name}\n"
        f"Описание: {description}\n"
        f"Цена: {price} руб.\n"
    )

    try:
        quantity = int(text)
        if price <= 0:
            msg += "\nКоличество быть целым числом больше 0"
            await bot.edit_message_text(
                text=msg,
                message_id=message_id,
                chat_id=chat_id
            )
            return
    except ValueError:
        msg += "\nКоличество должно быть числом"
        await bot.edit_message_text(
            text=msg,
            message_id=message_id,
            chat_id=chat_id
        )
        return

    await state.update_data(quantity=quantity)

    msg += (
        f"Количество: {quantity} шт.\n\n"
        "подтвердите или отмените создание товара"
    )

    keyboard_rules = [AdminConfirmCreateProductKeyboard()]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await bot.edit_message_text(
        text=msg,
        message_id=message_id,
        chat_id=chat_id,
        reply_markup=keyboard
    )

    await state.set_state(CreateProductState.confirm)


@admin_product_router.callback_query(CreateProductState.confirm, AdmCreateProductConfirmCallbackFactory.filter())
async def create_product_wait_confirm_hnd(
    callback: CallbackQuery,
    callback_data: AdmCreateProductConfirmCallbackFactory,
    state: FSMContext,
    product_service: FromDishka[ProductServicePort]
):

    if not callback_data.confirm:
        await state.clear()
        await callback.message.edit_text("Создание товара отменено")
        return

    data = await state.get_data()

    category_id = data.get("category_id")
    name = data.get("name")
    description = data.get("description")
    price = data.get("price")
    quantity = data.get("quantity")

    product_data = ProductSchemaCreate(
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        quantity=quantity,
    )

    log.info("Try to create product", product_data=product_data)
    try:
        created_product = await product_service.create_product(
            product_data=product_data
        )
    except Exception as e:
        log.error("Error on create_product_wait_confirm_hnd", exc_info=True)
        await callback.message.edit_text("Ошибка при создании товара")
        await state.clear()
        return

    keyboard_rules = [AdminProductSettingsKeyboard(created_product.id)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    msg = build_product_view(created_product)

    if created_product.image:
        image_path = product_image_path + created_product.image
    else:
        image_path = default_product_image_path
    image = await get_media_obj(image_path=image_path, caption=msg)

    await callback.message.edit_media(
        media=image,
        reply_markup=keyboard
    )

    await state.clear()

