from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

WORKDIR = Path(__file__).parent.parent

product_image_path = str(WORKDIR) + "/static/product_images/"
default_product_image_path = product_image_path + "default_image.jpg"

env_path = WORKDIR.parent

class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f"{env_path}/.env", extra="ignore")


class BotSettings(EnvBaseSettings):
    BOT_TOKEN: str
    ADMIN_TG_ID: int


class DBSettings(EnvBaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        # postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class RedisSettings(EnvBaseSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASS: str | None = None
    REDIS_DB: int = 0

    # REDIS_DATABASE: int = 1
    # REDIS_USERNAME: int | None = None
    # REDIS_TTL_STATE: int | None = None
    # REDIS_TTL_DATA: int | None = None

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASS:
            return f"redis://{self.REDIS_PASS}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class Settings(
    RedisSettings,
    DBSettings,
    BotSettings,
): ...



settings = Settings()