"""
Точка входа FastAPI: создание приложения и запуск uvicorn.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api import v1_router
from config import settings
from exceptions import APIException, InternalError
from loger_init import setup_logger

logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: движок БД и фабрика сессий."""
    engine = create_async_engine(settings.get_url_pg)
    app.state.engine = engine
    app.state.async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    yield
    await engine.dispose()


app = FastAPI(
    title="Organizations API",
    lifespan=lifespan,
)
app.include_router(v1_router)


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Преобразование доменных исключений в HTTP-ответ и логирование."""
    http_exc = exc.to_http_exception()
    if http_exc.status_code >= 500:
        logger.error(
            "APIException 5xx: %s - %s",
            type(exc).__name__,
            exc,
            extra={"status_code": http_exc.status_code, "detail": http_exc.detail},
        )
    else:
        logger.warning(
            "APIException 4xx: %s - %s",
            type(exc).__name__,
            exc,
            extra={"status_code": http_exc.status_code, "detail": http_exc.detail},
        )
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Необработанное исключение → 500 и запись в лог с трейсбеком."""
    logger.exception("Unhandled exception (500): %s - %s", type(exc).__name__, exc)
    http_exc = InternalError(
        "Internal server error",
        details={"type": type(exc).__name__},
    ).to_http_exception()
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
    )


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {"message": "Organizations API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
