"""Эндпоинт выдачи access-токена."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings
from secure import TokenService, get_token_service

router = APIRouter(prefix="/auth", tags=["Аутентификация"])
_credentials = HTTPBearer(auto_error=False)


@router.post(
    "/token",
    summary="Получить access-токен",
    description="Возвращает JWT (срок жизни в TOKEN_EXPIRE_SECONDS). При заданном API_KEY передайте его в заголовке Authorization: Bearer <api_key>.",
)
def create_access_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_credentials)],
    token_service: TokenService = Depends(get_token_service),
) -> dict[str, str]:
    """Выдать JWT. Если в настройках задан API_KEY — в Authorization: Bearer должен быть тот же ключ."""
    if settings.API_KEY:
        if credentials is None or credentials.credentials != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный или отсутствующий Authorization",
                headers={"WWW-Authenticate": "Bearer"},
            )
    token = token_service.create_token()
    return {"access_token": token, "token_type": "bearer"}
