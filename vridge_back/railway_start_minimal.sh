#!/bin/bash
# Railway 최소 시작 스크립트 - 헬스체크 우선

echo "[INFO] Railway 최소 배포 시작"
echo "[INFO] PORT: $PORT"

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=config.settings.railway

# 즉시 Gunicorn 시작 (마이그레이션 없이)
echo "[INFO] Gunicorn 즉시 시작..."
gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -