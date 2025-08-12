#!/bin/bash
# Railway 배포용 시작 스크립트
# 헬스체크를 위한 임시 서버 실행 후 실제 Django 서버 시작

echo "[INFO] Starting Railway deployment..."
echo "[INFO] Environment: RAILWAY_ENVIRONMENT=${RAILWAY_ENVIRONMENT}"
echo "[INFO] Port: ${PORT}"

# Railway 환경 변수 설정
export DJANGO_SETTINGS_MODULE=config.settings.railway
export RAILWAY_DEPLOYMENT=true

# 헬스체크 서버를 백그라운드에서 실행
echo "[INFO] Starting health check server on port ${PORT}..."
python3 railway_health.py &
HEALTH_PID=$!

# 헬스체크 서버가 시작될 때까지 대기
sleep 3

# 데이터베이스 연결 테스트
echo "[INFO] Testing database connection..."
python3 -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
import django
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
    print('[SUCCESS] Database connection successful')
except Exception as e:
    print(f'[WARNING] Database connection failed: {e}')
    sys.exit(0)  # Continue anyway
"

# 데이터베이스 마이그레이션 실행
echo "[INFO] Running database migrations..."
python3 manage.py migrate --noinput || echo "[WARNING] Migration failed but continuing"

# 정적 파일 수집
echo "[INFO] Collecting static files..."
python3 manage.py collectstatic --noinput || echo "[WARNING] Collectstatic failed but continuing"

# 캐시 테이블 생성 (필요한 경우)
echo "[INFO] Creating cache table if needed..."
python3 manage.py createcachetable 2>/dev/null || true

# 헬스체크 서버 종료
echo "[INFO] Stopping health check server..."
kill $HEALTH_PID 2>/dev/null || true
sleep 1

# Gunicorn으로 실제 Django 서버 시작
echo "[INFO] Starting Gunicorn server on port ${PORT}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --threads 2 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output