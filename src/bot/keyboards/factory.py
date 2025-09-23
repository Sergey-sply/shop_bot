from src.bot.keyboards.core import AbstractTelegramKeyboard

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, ReplyKeyboardMarkup

def combine_keyboards(keyboards: list[AbstractTelegramKeyboard], builder: InlineKeyboardBuilder) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
    for keyboard in keyboards:
        keyboard.generate_keyboard(builder)
    return builder.as_markup()