from aiogram.fsm.state import StatesGroup, State


class UpdateProductState(StatesGroup):
    wait_value = State()


class CreateProductState(StatesGroup):
    category = State()
    name = State()
    description = State()
    image = State()
    price = State()
    quantity = State()
    confirm = State()


class ChangeImageProductState(StatesGroup):
    image = State()