#!/bin/bash
# Railway 배포용 단순화된 시작 스크립트

echo "[INFO] Starting Railway deployment (simplified)..."
echo "[INFO] Port: ${PORT}"

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=config.settings.railway
export PYTHONUNBUFFERED=1

# 데이터베이스 마이그레이션
echo "[INFO] Running migrations..."
python3 manage.py migrate --noinput || echo "[WARNING] Migration failed"

# 정적 파일 수집
echo "[INFO] Collecting static files..."
python3 manage.py collectstatic --noinput || echo "[WARNING] Collectstatic failed"

# Gunicorn 시작 (단순화된 설정)
echo "[INFO] Starting Gunicorn on port ${PORT}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    --preload