"""Базовая Pydantic-схема: общая конфигурация для ORM и API."""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Базовый класс для всех схем; включает режим from_attributes для ответов из моделей БД."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_default=True,
    )
