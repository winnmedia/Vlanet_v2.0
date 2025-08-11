#!/bin/bash

echo "Starting emergency server..."

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=config.settings.railway
export PYTHONUNBUFFERED=1
export DJANGO_LOG_LEVEL=ERROR

# 포트 확인
PORT=${PORT:-8000}
echo "Port: $PORT"

# 간단한 마이그레이션 시도 (실패해도 계속)
python manage.py migrate --noinput 2>/dev/null || echo "Migration skipped"

# Gunicorn 시작 (최소 설정)
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --log-level ERROR \
    --preload