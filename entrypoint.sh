#!/bin/sh
set -e

cd /app/src
export PYTHONPATH=/app/src

echo "Running migrations..."
uv run alembic upgrade head

echo "Seeding test data..."
uv run python -m test_data

echo "Starting application..."
cd /app
exec uv run uvicorn main:app --host 0.0.0.0 --port 8000
