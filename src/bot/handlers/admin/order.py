from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka

from src.application.ports.services.order import OrderServicePort
from src.application.use_cases.order.update import UpdateOrderStatusUseCase
from src.bot.callback.admin.order import AdmOrderIDCallbackFactory, AdmOrderUpdateStatusCallbackFactory, \
    AdmOrderStatusCallbackFactory, AdmOrderCancelUpdateStatusCallbackFactory, AdmOrderListCallbackFactory
from src.bot.filters.role import RoleFilter
from src.bot.handlers.builds.order import build_order_view
from src.bot.handlers.prompts import ORDER_STATUS_PROMPTS
from src.bot.keyboards.admin.order import AdminOrderListKeyboard, AdminOrderInfoKeyboard, AdminOrderStatusKeyboard
from src.bot.keyboards.factory import combine_keyboards
from src.bot.const import BASE_PER_PAGE
from src.core.enums.order import OrderStatus

admin_order_router = Router()
admin_order_router.message.filter(RoleFilter(required_role="admin"))

@admin_order_router.callback_query(AdmOrderListCallbackFactory.filter())
async def order_list_adm_hnd(
    callback: CallbackQuery,
    callback_data: AdmOrderListCallbackFactory,
    order_service: FromDishka[OrderServicePort]
):

    orders = await order_service.get_orders(
        page=callback_data.page,
        per_page=BASE_PER_PAGE
    )

    if orders is None:
        await callback.answer("Заказов пока нет")
        return

    msg = "Заказы"

    keyboard_rules = [AdminOrderListKeyboard(orders)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )


@admin_order_router.callback_query(AdmOrderIDCallbackFactory.filter())
async def order_info_adm_hnd(
    callback: CallbackQuery,
    callback_data: AdmOrderIDCallbackFactory,
    order_service: FromDishka[OrderServicePort]
):
    order_info = await order_service.get_order_full_info(order_id=callback_data.order_id)

    msg = f"ID клиента: {order_info.user_id}\n"
    msg += build_order_view(order_info)

    keyboard_rules = [
        AdminOrderInfoKeyboard(
            order_id=order_info.order_id,
            actual_status=order_info.order_status.value
        )
    ]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )


@admin_order_router.callback_query(AdmOrderUpdateStatusCallbackFactory.filter())
async def order_status_update_hnd(
    callback: CallbackQuery,
    callback_data: AdmOrderUpdateStatusCallbackFactory
):
    statuses = ORDER_STATUS_PROMPTS.copy()

    statuses.pop(callback_data.actual_status)

    keyboard_rules = [AdminOrderStatusKeyboard(statuses=statuses, order_id=callback_data.order_id)]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())


    await callback.message.edit_reply_markup(
        reply_markup=keyboard
    )


@admin_order_router.callback_query(AdmOrderStatusCallbackFactory.filter())
async def order_status_selected_hnd(
    callback: CallbackQuery,
    callback_data: AdmOrderStatusCallbackFactory,
    order_update_status_uc: FromDishka[UpdateOrderStatusUseCase]
):

    status = OrderStatus(callback_data.status)
    updated_order = await order_update_status_uc(
        order_id=callback_data.order_id,
        status=status
    )
    await callback.answer("Статус успешно обновлен")

    msg = f"ID клиента: {updated_order.user_id}\n"
    msg += build_order_view(updated_order)

    keyboard_rules = [
        AdminOrderInfoKeyboard(
            order_id=updated_order.order_id,
            actual_status=updated_order.order_status.value
        )
    ]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())


    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )


@admin_order_router.callback_query(AdmOrderCancelUpdateStatusCallbackFactory.filter())
async def cancel_update_order_status_hnd(
    callback: CallbackQuery,
    callback_data: AdmOrderCancelUpdateStatusCallbackFactory,
    order_service: FromDishka[OrderServicePort]
):
    order_info = await order_service.get_order_full_info(order_id=callback_data.order_id)

    msg = f"ID клиента: {order_info.user_id}\n"
    msg += build_order_view(order_info)

    keyboard_rules = [
        AdminOrderInfoKeyboard(
            order_id=order_info.order_id,
            actual_status=order_info.order_status.value
        )
    ]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await callback.message.edit_text(
        text=msg,
        reply_markup=keyboard
    )

