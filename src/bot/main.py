import asyncio

from aiogram import Dispatcher
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka

from src.bot.handlers import register_handlers
from src.bot.middlewares import register_middlewares
from src.bot.utils.setup_bot import setup_bot
from src.bot.utils.setup_dispatcher import setup_dispatcher
from src.infrastructure.database.db import db_on_startup
from src.infrastructure.di.setup_dishka import ioc_factory
from src.infrastructure.logging.config import configure_logging, get_logger


async def run() -> None:
    configure_logging()
    log = get_logger(__name__)

    log.info("Starting")

    await db_on_startup()

    container: AsyncContainer = ioc_factory()

    bot = await setup_bot()

    dp: Dispatcher = await setup_dispatcher()

    setup_dishka(container=container, router=dp, auto_inject=True)

    register_middlewares(dp, container)
    register_handlers(dp)

    allowed = dp.resolve_used_update_types()
    try:
        log.info("Success startup")
        await dp.start_polling(
            bot,
            allowed_updates=allowed,
            close_bot_session=True,
        )
    finally:
        log.info("Graceful shutdown")
        await container.close()


if __name__ == "__main__":
    asyncio.run(run())