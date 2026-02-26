"""Конфигурация приложения из переменных окружения."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки: логирование и параметры подключения к PostgreSQL."""

    LOGGER_LVL: str = 'INFO'

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_SECONDS: int = 1200  # 20 минут
    API_KEY: str = ""  # ключ для получения токена

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @property
    def get_url_pg(self) -> str:
        """URL для асинхронного подключения к PostgreSQL."""
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    model_config = SettingsConfigDict(env_file='../.env')

settings = Settings()
