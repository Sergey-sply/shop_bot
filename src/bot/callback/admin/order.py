from aiogram.filters.callback_data import CallbackData

from src.bot.callback.base import BasePageCallback


class AdmOrderIDCallbackFactory(CallbackData, prefix="adm_orderID"):
    order_id: str


class AdmOrderListCallbackFactory(BasePageCallback, prefix="adm_orders"): ...


class AdmOrderUpdateStatusCallbackFactory(CallbackData, prefix="adm_upd_status"):
    order_id: str
    actual_status: str

class AdmOrderStatusCallbackFactory(CallbackData, prefix="adm_order_status"):
    status: str
    order_id: str

class AdmOrderCancelUpdateStatusCallbackFactory(CallbackData, prefix="cancel_upd_order_status"):
    order_id: str


class AdmStartCallbackFactory(CallbackData, prefix="adm_start"): ...