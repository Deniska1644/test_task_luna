"""Зависимости FastAPI для проверки Bearer-токена."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .token_service import TokenService

_security = HTTPBearer(auto_error=False)


def get_token_service() -> TokenService:
    """Фабрика для внедрения TokenService в зависимости FastAPI."""
    return TokenService()


def require_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_security)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> dict:
    """Зависимость: проверяет заголовок Authorization Bearer и возвращает payload токена."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется заголовок Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = token_service.verify_token(credentials.credentials)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
