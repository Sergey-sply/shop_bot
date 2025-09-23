
from aiogram import Dispatcher
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import setup_dishka

from src.infrastructure.di.providers import UseCaseProvider, ServiceProvider, RepositoryProvider
from src.infrastructure.logging.config import get_logger

log = get_logger(__name__)

def ioc_factory() -> AsyncContainer:
    container = make_async_container(
        RepositoryProvider(),
        ServiceProvider(),
        UseCaseProvider()
    )
    return container


def init_di(dp: Dispatcher, container: AsyncContainer) -> None:
    log.info("Setup dishka")
    setup_dishka(container, router=dp, auto_inject=True)
