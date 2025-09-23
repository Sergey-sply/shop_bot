from aiogram.filters.callback_data import CallbackData


class CreateOrderCallbackFactory(CallbackData, prefix="create_order"): ...


class OrderDMIDCallbackFactory(CallbackData, prefix="order_DM"):
    delivery_method_id: int
    delivery_method_name: str


class ConfirmOrderCallbackFactory(CallbackData, prefix="confirm_order"):
    confirm: bool

class OrderIDCallbackFactory(CallbackData, prefix="orderID"):
    order_id: str

class OrderListCallbackFactory(CallbackData, prefix="us_order_list"): ...