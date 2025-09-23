from aiogram import Dispatcher
from dishka import AsyncContainer

from src.bot.middlewares.auth import AuthMiddleware
from src.bot.middlewares.tracer import TraceIDAiogramMiddleware


def register_middlewares(dp: Dispatcher, container: AsyncContainer):
    dp.message.middleware(AuthMiddleware(container))

    # bind ctx vars to logger
    dp.message.middleware(TraceIDAiogramMiddleware())
    dp.callback_query.middleware(TraceIDAiogramMiddleware())

    return dp