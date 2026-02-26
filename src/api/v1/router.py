"""Роутер API v1: подключение всех подроутеров."""

from fastapi import APIRouter, Depends

from secure import require_token

from .area import router as area_router
from .auth import router as auth_router
from .buildings import router as buildings_router
from .health import router as health_router
from .organizations import router as organizations_router

router = APIRouter(prefix="/api/v1")

# Без токена: health и выдача токена
router.include_router(health_router)
router.include_router(auth_router)

# С проверкой Bearer-токена
router.include_router(organizations_router, dependencies=[Depends(require_token)])
router.include_router(buildings_router, dependencies=[Depends(require_token)])
router.include_router(area_router, dependencies=[Depends(require_token)])
