#!/bin/bash
set -e

echo "=== VideoPlanet Backend Starting ==="
echo "Time: $(date)"

# 환경변수 설정
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"config.settings.railway"}
export PORT=${PORT:-"8000"}

echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "PORT: $PORT"

# 마이그레이션 (에러 무시)
python3 manage.py migrate --noinput || echo "Migration skipped"

# 정적 파일 수집
python3 manage.py collectstatic --noinput || echo "Static files skipped"

# Gunicorn 시작 (간단한 설정)
echo "Starting Gunicorn on port $PORT..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 30 \
    --log-level info