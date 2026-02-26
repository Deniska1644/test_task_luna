"""Сервис выдачи и валидации JWT-токенов."""

import time
from typing import Any

import jwt

from config import settings


class TokenService:
    """Выдача и проверка access-токенов (JWT, срок жизни в секундах)."""

    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        expire_seconds: int | None = None,
    ) -> None:
        self.secret_key = secret_key or settings.SECRET_KEY
        self.algorithm = algorithm or settings.JWT_ALGORITHM
        self.expire_seconds = expire_seconds or settings.TOKEN_EXPIRE_SECONDS

    def create_token(self, subject: str = "api", extra: dict[str, Any] | None = None) -> str:
        """Создать JWT с истечением через TOKEN_EXPIRE_SECONDS секунд."""
        now = int(time.time())
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + self.expire_seconds,
            **(extra or {}),
        }
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm,
        )

    def verify_token(self, token: str) -> dict[str, Any]:
        """Проверить токен и вернуть payload; при ошибке — исключение."""
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
        )
