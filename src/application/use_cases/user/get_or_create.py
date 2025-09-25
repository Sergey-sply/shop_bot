from structlog import get_logger

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.ports.services.user import UserServicePort
from src.application.schemas.user import UserSchemaCreate

log = get_logger(__name__)

class GetOrCreateUserUseCase:
    def __init__(
        self,
        user_service: UserServicePort,
        session_maker: async_sessionmaker[AsyncSession]
    ):
        self.__user_service = user_service
        self.__session_maker = session_maker

    async def __call__(self, user_data: UserSchemaCreate) -> bool:
        async with self.__session_maker() as session:
            async with session.begin():
                try:
                    if not await self.__user_service.exist_by_id(user_data.id, session=session):
                        await self.__user_service.create_user(user_data, session=session)
                        return True
                    return False
                except Exception as e:
                    log.error("Error on GetOrCreateUserUseCase", exc_info=True)
                    raise e

