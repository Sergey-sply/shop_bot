from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.db import async_session_maker_ctx


def use_session(func):
    async def wrapper(self, *args, session: AsyncSession | None = None, **kwargs):  # todo: fix work only with kw
        if session is not None or session in kwargs:
            return await func(self, *args, session=session, **kwargs)

        _session_maker = async_session_maker_ctx.get()
        async with _session_maker() as session:
            async with session.begin():
                return await func(self, *args, session=session, **kwargs)
    return wrapper
