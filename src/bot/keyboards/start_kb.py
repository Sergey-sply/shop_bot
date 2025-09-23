from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_kb():
    main_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Товары"),
            ],
            [
                KeyboardButton(text="Корзина"),
                KeyboardButton(text="Заказы"),
            ],

        ],
        resize_keyboard=True,
    )
    return main_kb