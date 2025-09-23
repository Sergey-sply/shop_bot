from redis.asyncio import Redis, ConnectionPool

from src.config.settings import settings

redis_client = Redis(
    connection_pool=ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASS,
        db=settings.REDIS_DB,
        max_connections=5,
        health_check_interval=30,
    ),
    decode_responses=True,
    encoding='utf-8',

)

