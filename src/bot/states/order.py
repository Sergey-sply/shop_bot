from aiogram.fsm.state import StatesGroup, State


class CreateOrderState(StatesGroup):
    full_name = State()
    address = State()
    phone_number = State()
    delivery_method = State()
    confirm = State()
