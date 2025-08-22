#!/bin/sh
set -e

echo "[start] Starting backend services..."

echo "[wait] Waiting for Qdrant to be ready..."
# Qdrant가 준비될 때까지 대기
for i in $(seq 1 30); do
  if curl -f http://qdrant:6333/collections >/dev/null 2>&1; then
    echo "[ok] Qdrant is ready."
    break
  fi
  echo "  - retry $i/30"
  sleep 2
done

echo "[django] migrate"
python manage.py migrate --noinput

echo "[qdrant] ensure collection"
python manage.py qdrant_init

echo "[django] collectstatic"
python manage.py collectstatic --noinput

echo "[uvicorn] start"
uvicorn config.asgi:application --host 0.0.0.0 --port 8000 