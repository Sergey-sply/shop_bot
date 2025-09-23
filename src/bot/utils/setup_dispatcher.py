from aiogram import Dispatcher
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from dishka import AsyncContainer

from src.bot.handlers import register_handlers
from src.bot.middlewares import register_middlewares
from src.infrastructure.cache.redis.setup_redis import redis_client



async def setup_dispatcher() -> Dispatcher:
    dp: Dispatcher = Dispatcher(
        storage=RedisStorage(redis=redis_client, key_builder=DefaultKeyBuilder())
    )

    return dp


__all__ = ["setup_dispatcher"]
