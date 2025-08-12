#!/bin/bash
# Railway 안전 배포 스크립트 - 헬스체크 보장

echo "================================================"
echo "[RAILWAY] 안전 배포 시작 - $(date)"
echo "================================================"

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=config.settings.railway
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

echo "[INFO] PORT: $PORT"

# 간단한 Django 확인
echo "[INFO] Django 설정 확인..."
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
import django
django.setup()
print('[OK] Django 설정 로드 성공')
" || echo "[WARNING] Django 설정 경고 (계속 진행)"

# 마이그레이션 (실패해도 계속)
echo "[INFO] 마이그레이션 시도..."
python3 manage.py migrate --noinput 2>&1 | head -20 || echo "[WARNING] 마이그레이션 경고"

# 정적 파일 수집 (실패해도 계속)
echo "[INFO] 정적 파일 수집..."
python3 manage.py collectstatic --noinput 2>&1 | head -10 || echo "[WARNING] 정적 파일 경고"

# Gunicorn 시작 (최소 설정)
echo "[INFO] Gunicorn 시작 (포트 $PORT)..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info