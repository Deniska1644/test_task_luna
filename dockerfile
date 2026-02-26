# Сборка и запуск приложения с установкой зависимостей через uv
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
RUN pip install uv \
    && uv sync --no-dev

COPY src ./src
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

ENV PYTHONPATH=/app/src
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
