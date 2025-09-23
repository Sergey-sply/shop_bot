from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.services.user import UserServicePort
from src.infrastructure.database.decorators import use_session
from src.infrastructure.logging.config import get_logger
from src.application.schemas.user import UserSchemaCreate

log = get_logger(__name__)

class GetOrCreateUserUseCase:
    def __init__(self, user_service: UserServicePort):
        self.__user_service = user_service

    @use_session
    async def __call__(self, user_data: UserSchemaCreate, session: AsyncSession | None) -> bool:
        try:
            if not await self.__user_service.exist_by_id(user_data.id, session=session):
                await self.__user_service.create_user(user_data, session=session)
                return True
            return False
        except Exception as e:
            log.error("Error on GetOrCreateUserUseCase", exc_info=True)
            raise e

