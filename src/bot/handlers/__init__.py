from aiogram import Dispatcher

from src.bot.handlers.admin.base import admin_panel_router
from src.bot.handlers.admin.order import admin_order_router
from src.bot.handlers.admin.product import admin_product_router
from src.bot.handlers.user.cart import cart_router
from src.bot.handlers.user.catalog import catalog_router
from src.bot.handlers.user.order import order_router
from src.bot.handlers.user.start import start_router


def register_handlers(dp: Dispatcher) -> Dispatcher:
    dp.include_router(cart_router)
    dp.include_router(catalog_router)
    dp.include_router(order_router)
    dp.include_router(start_router)

    dp.include_router(admin_panel_router)
    dp.include_router(admin_order_router)
    dp.include_router(admin_product_router)


    return dp

__all__ = ["register_handlers"]