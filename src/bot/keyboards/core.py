import abc

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class AbstractTelegramKeyboard(abc.ABC):
    @abc.abstractmethod
    def generate_keyboard(
            self,
            builder: InlineKeyboardBuilder | ReplyKeyboardBuilder, *args, **kwargs
    ) -> None:
        raise NotImplementedError
