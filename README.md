# Organizations API

REST API для работы с организациями, зданиями и видами деятельности. FastAPI, PostgreSQL, JWT-авторизация.

## Стек

- **Python 3.12**, FastAPI, SQLAlchemy 2 (async), Pydantic
- **PostgreSQL 16**, asyncpg
- **JWT** (PyJWT) для access-токенов
- **Alembic** — миграции

## Требования

- Python 3.12+
- PostgreSQL 16 (или Docker)
- [uv](https://docs.astral.sh/uv/) для управления зависимостями

## Установка и запуск

### Локально

1. Клонировать репозиторий, перейти в каталог проекта.

2. Создать виртуальное окружение и установить зависимости:

   ```bash
   uv sync
   ```

3. Скопировать пример конфигурации и задать переменные окружения:

   ```bash
   cp .envexample .env
   ```

   В `.env` указать параметры БД и при необходимости `SECRET_KEY`, `API_KEY` (см. раздел «Переменные окружения»).

4. Запустить PostgreSQL (локально или в Docker), применить миграции и сиды:

   ```bash
   uv run alembic -c src/alembic.ini upgrade head
   uv run python -m src.test_data
   ```

5. Запустить приложение:

   ```bash
   uv run uvicorn main:app --reload --app-dir src
   ```

   API будет доступно по адресу: http://localhost:8000  
   Документация: http://localhost:8000/docs

### Docker

```bash
cp .envexample .env
docker compose up -d
```

При старте контейнера `app` автоматически выполняются миграции и загрузка тестовых данных, затем запускается uvicorn.

- Приложение: http://localhost:8000  
- Порт приложения можно изменить через переменную `APP_PORT` в `.env`.

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `POSTGRES_HOST` | Хост PostgreSQL | — |
| `POSTGRES_PORT` | Порт PostgreSQL | `5432` |
| `POSTGRES_DB` | Имя БД | — |
| `POSTGRES_USER` | Пользователь БД | — |
| `POSTGRES_PASSWORD` | Пароль БД | — |
| `LOGGER_LVL` | Уровень логирования | `INFO` |
| `SECRET_KEY` | Секрет для подписи JWT | `change-me-in-production` |
| `JWT_ALGORITHM` | Алгоритм JWT | `HS256` |
| `TOKEN_EXPIRE_SECONDS` | Время жизни токена (сек) | `1200` (20 мин) |
| `API_KEY` | Ключ для выдачи токена (если пусто — не проверяется) | — |

## API

### Без авторизации

- **GET /** — метаинформация и ссылка на docs  
- **GET /api/v1/health** — healthcheck  
- **POST /api/v1/auth/token** — выдача JWT  
  - При заданном `API_KEY`: заголовок `Authorization: Bearer <api_key>`  
  - Ответ: `{"access_token": "<jwt>", "token_type": "bearer"}`

### С авторизацией (Bearer JWT)

Все остальные эндпоинты требуют заголовок:

```http
Authorization: Bearer <access_token>
```

- **Организации**
  - `GET /api/v1/organizations?activity_id=<id>` или `?activity_name=<name>` — список по виду деятельности
  - `GET /api/v1/organizations/search?name=<строка>` — поиск по названию
  - `GET /api/v1/organizations/{id}` — детали организации (адреса, виды деятельности)

- **Здания**
  - `GET /api/v1/buildings/{id}/organizations` — здание и список организаций в нём

- **Геопоиск**
  - `GET /api/v1/area/radius?lat=&lon=&radius_km=` — по радиусу от точки
  - `GET /api/v1/area/bbox?min_lat=&max_lat=&min_lon=&max_lon=` — по прямоугольнику

Полное описание запросов и ответов — в Swagger UI: http://localhost:8000/docs

