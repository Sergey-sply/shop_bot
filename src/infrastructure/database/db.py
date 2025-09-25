import contextvars
from typing import Callable

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.config.settings import settings
from src.database.models import Base

AsyncSessionMaker = Callable[[], AsyncSession]
async_session_maker_ctx = contextvars.ContextVar[AsyncSessionMaker]("async_session_maker")

async_engine = create_async_engine(
    settings.DATABASE_URL_asyncpg,
    echo=False,
    future=True,
)
async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)


async def check_db_connection():
    try:
        async with async_engine.connect() as conn:
            r = await conn.execute("SELECT 1")
            print(r)
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")


async def db_on_startup():
    async_session_maker_ctx.set(async_session_maker)


async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)