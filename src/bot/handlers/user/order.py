from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dishka import FromDishka

from src.application.ports.services.cart import CartServicePort
from src.application.ports.services.delivery_method import DeliveryMethodServicePort
from src.application.ports.services.order import OrderServicePort
from src.application.use_cases.order.create import CreateOrderUseCase
from src.bot.callback.user.order import CreateOrderCallbackFactory, OrderDMIDCallbackFactory, \
    ConfirmOrderCallbackFactory, OrderIDCallbackFactory, OrderListCallbackFactory
from src.bot.handlers.builds.order import build_order_view
from src.bot.keyboards.factory import combine_keyboards
from src.bot.keyboards.user.order import DeliveryMethodsListKeyboard, ConfirmOrderKeyboard, OrderInfoKeyboard, \
    UserOrdersListKeyboard
from src.bot.states.order import CreateOrderState
from src.core.exceptions.order import OutOfStock, EmptyUserCart
from src.application.schemas.order import OrderSchemaCreate

order_router = Router()

@order_router.callback_query(CreateOrderCallbackFactory.filter())
async def create_order_hnd(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.message.edit_text(
        text="Укажите Ваше ФИО"
    )
    await state.set_state(CreateOrderState.full_name)


@order_router.message(CreateOrderState.full_name)
async def create_order_wait_for_fn_hnd(
    message: Message,
    state: FSMContext
):
    full_name = message.text
    await state.update_data(
        full_name=full_name
    )
    await message.answer(
        text="Укажите адрес доставки"
    )
    await state.set_state(CreateOrderState.address)


@order_router.message(CreateOrderState.address)
async def create_order_wait_for_adr_hnd(
    message: Message,
    state: FSMContext
):
    address = message.text
    await state.update_data(
        address=address
    )
    await message.answer(
        text="Укажите Ваш номер телефона"
    )
    await state.set_state(CreateOrderState.phone_number)


@order_router.message(CreateOrderState.phone_number)
async def create_order_wait_for_ph_hnd(
    message: Message,
    state: FSMContext,
    delivery_service: FromDishka[DeliveryMethodServicePort]
):
    phone_number = message.text
    await state.update_data(
        phone_number=phone_number
    )

    delivery_methods = await delivery_service.get_delivery_methods()

    keyboard_rules = [DeliveryMethodsListKeyboard(delivery_methods)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await message.answer(
        "Выберите способ доставки",
        reply_markup=keyboard
    )
    await state.set_state(CreateOrderState.delivery_method)


@order_router.callback_query(CreateOrderState.delivery_method, OrderDMIDCallbackFactory.filter())
async def create_order_wait_for_dm_hnd(
    callback: CallbackQuery,
    callback_data: OrderDMIDCallbackFactory,
    cart_service: FromDishka[CartServicePort],
    state: FSMContext
):
    await state.update_data(delivery_method_id=callback_data.delivery_method_id)
    data = await state.get_data()
    full_name = data.get("full_name")
    address = data.get("address")
    phone_num = data.get("phone_number")

    cart_cost = await cart_service.get_user_cart_cost(callback.message.chat.id)


    msg = (
        f"Подтверждение заказа\n"
        f"ФИО: {full_name}\n"
        f"Адрес доставки: {address}\n"
        f"Номер телефона: {phone_num}\n"
        f"Способ доставки: {callback_data.delivery_method_name}\n\n"
        f"Итоговая стоимость: {cart_cost} руб."
    )

    keyboard_rules = [ConfirmOrderKeyboard()]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )
    await state.set_state(CreateOrderState.confirm)


@order_router.callback_query(CreateOrderState.confirm, ConfirmOrderCallbackFactory.filter())
async def create_order_confirm_hnd(
    callback: CallbackQuery,
    callback_data: ConfirmOrderCallbackFactory,
    state: FSMContext,
    create_order: FromDishka[CreateOrderUseCase]
):

    if not callback_data.confirm:
        await callback.message.edit_text("Оформление заказа отменено")
        await state.clear()
        return

    data = await state.get_data()
    full_name = data.get("full_name")
    address = data.get("address")
    phone_num = data.get("phone_number")
    delivery_method_id = data.get("delivery_method_id")

    order_data = OrderSchemaCreate(
        user_id=callback.message.chat.id,
        delivery_method_id=delivery_method_id,
        client_name=full_name,
        client_number=phone_num,
        client_address=address
    )
    try:
        order_info = await create_order(order_data)
    except OutOfStock as oos_ex:
        msg = "Недостаточно товара на складе!\n"
        for product in oos_ex.stock_ex:
            msg += (
                f"Товар: {product.get("product_name")}\n"
                f"Нужно: {product.get('need')}\n"
                f"В наличии: {product.get('stock')}\n\n"
            )
        await callback.message.edit_text(
            text=msg
        )
        await state.clear()
        return

    except EmptyUserCart as euc_ex:
        msg = "Ваша корзина пуста."
        await callback.message.edit_text(
            text=msg
        )
        await state.clear()
        return

    msg = f"Заказ успешно создан!\n"
    msg += build_order_view(order_info)

    await callback.message.edit_text(
        text=msg
    )

    await state.clear()


@order_router.message(F.text == "Заказы")
async def user_orders_hnd(
    message: Message,
    order_service: FromDishka[OrderServicePort]
):
    orders = await order_service.get_user_orders(user_id=message.from_user.id)

    if not orders:
        await message.answer("У вас нет заказов")
        return

    msg = "Ваши заказы:\n"

    keyboard_rules = [UserOrdersListKeyboard(orders)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await message.answer(
        text=msg,
        reply_markup=keyboard
    )

@order_router.callback_query(OrderListCallbackFactory.filter())
async def user_orders_clb(
    callback: CallbackQuery,
    order_service: FromDishka[OrderServicePort]
):
    orders = await order_service.get_user_orders(user_id=callback.message.chat.id)

    if not orders:
        await callback.message.edit_text("У вас нет заказов")
        return

    msg = "Ваши заказы:\n"

    keyboard_rules = [UserOrdersListKeyboard(orders)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )


@order_router.callback_query(OrderIDCallbackFactory.filter())
async def user_order_info_hnd(
    callback: CallbackQuery,
    callback_data: OrderIDCallbackFactory,
    order_service: FromDishka[OrderServicePort]
):
    order_info = await order_service.get_order_full_info(
        order_id=callback_data.order_id
    )

    if order_info is None:
        await callback.answer("Заказа не существует")
        return

    msg = build_order_view(order_info)

    keyboard_rules = [OrderInfoKeyboard()]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )

