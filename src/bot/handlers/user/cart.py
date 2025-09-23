from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dishka import FromDishka

from src.application.ports.services.cart import CartServicePort
from src.bot.callback.user.cart import CartPageCallbackFactory, CartIDCallbackFactory, \
    ChangeCartItemQuantityCallbackFactory, DeleteCartItemCallbackFactory, DeleteCartCallbackFactory
from src.bot.handlers.builds.cart import build_cart_info_view, build_cart_list_view
from src.bot.keyboards.factory import combine_keyboards
from src.bot.keyboards.user.cart import UserCartListKeyboard
from src.bot.const import BASE_PER_PAGE


cart_router = Router()

@cart_router.message(F.text == "Корзина")
async def get_user_cart_hnd(message: Message, state: FSMContext, cart_service: FromDishka[CartServicePort]):
    await state.clear()
    carts = await cart_service.get_user_cart(
        page=1,
        per_page=BASE_PER_PAGE,
        user_id=message.from_user.id
    )
    if carts is None:
        await message.answer(
            text="Корзина пуста."
        )
        return

    msg = (
        f"Ваша корзина\n"
        f"Общая стоимость: {carts.total_amount} руб."
    )

    keyboard_rules = [UserCartListKeyboard(carts)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await message.answer(
        text=msg,
        reply_markup=keyboard
    )


@cart_router.callback_query(CartPageCallbackFactory.filter())
async def get_user_cart_clb(
    callback: CallbackQuery,
    callback_data: CartPageCallbackFactory,
    cart_service: FromDishka[CartServicePort]
):
    carts = await cart_service.get_user_cart(
        user_id=callback.message.chat.id,
        page=callback_data.page,
        per_page=BASE_PER_PAGE,
    )

    msg, keyboard = await build_cart_list_view(carts=carts)
    await callback.message.edit_text(text=msg, reply_markup=keyboard)


@cart_router.callback_query(CartIDCallbackFactory.filter())
async def get_user_cart_item_info_hnd(
    callback: CallbackQuery,
    callback_data: CartIDCallbackFactory,
    cart_service: FromDishka[CartServicePort]
):
    cart_info = await cart_service.get_cart_item_info(cart_id=callback_data.cart_id)

    if cart_info is None:
        await callback.answer("Товара нет в корзине")
        return

    msg, keyboard = build_cart_info_view(cart_info)

    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )


@cart_router.callback_query(ChangeCartItemQuantityCallbackFactory.filter())
async def change_cart_item_q_hnd(
    callback: CallbackQuery,
    callback_data: ChangeCartItemQuantityCallbackFactory,
    cart_service: FromDishka[CartServicePort]
):
    try:
        new_q = await cart_service.change_quantity(cart_id=callback_data.cart_id, quantity=callback_data.quantity)
        print(new_q, callback_data.prev_quantity)

        if new_q == 0:
            await callback.answer("Товар закончился")
            carts = await cart_service.get_user_cart(
                user_id=callback.message.chat.id,
                page=1,
                per_page=BASE_PER_PAGE,
            )
            msg, keyboard = await build_cart_list_view(carts)
        elif new_q == callback_data.prev_quantity:
            await callback.answer("Больше товаров в наличии нет")
            return
        else:
            cart_info = await cart_service.get_cart_item_info(cart_id=callback_data.cart_id)
            msg, keyboard = build_cart_info_view(cart_info)

        try:
            await callback.message.edit_text(
                text=msg,
                reply_markup=keyboard
            )
        except Exception as e:
            await callback.answer()
    except Exception as e:
        print(e)
        raise e



@cart_router.callback_query(DeleteCartItemCallbackFactory.filter())
async def delete_cart_item_hnd(
    callback: CallbackQuery,
    callback_data: DeleteCartItemCallbackFactory,
    cart_service: FromDishka[CartServicePort]
):
    await cart_service.delete_cart_by_id(cart_id=callback_data.cart_id)

    carts = await cart_service.get_user_cart(
        user_id=callback.message.chat.id,
        page=1,
        per_page=BASE_PER_PAGE,
    )
    await callback.answer("Товар успешно удален")
    msg, keyboard = await build_cart_list_view(carts)

    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )

@cart_router.callback_query(DeleteCartCallbackFactory.filter())
async def delete_user_cart_hnd(
    callback: CallbackQuery,
    callback_data: DeleteCartCallbackFactory,
    cart_service: FromDishka[CartServicePort]
):
    await cart_service.delete_all_user_carts(user_id=callback.message.chat.id)
    await callback.message.edit_text(
        text="Корзина успешно очищена!"
    )

