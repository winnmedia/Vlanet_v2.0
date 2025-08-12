#!/bin/bash
# Railway 배포용 시작 스크립트
# 헬스체크를 위한 임시 서버 실행 후 실제 Django 서버 시작

echo "[INFO] Starting Railway deployment..."

# 헬스체크 서버를 백그라운드에서 실행
echo "[INFO] Starting health check server..."
python3 railway_health.py &
HEALTH_PID=$!

# 헬스체크 서버가 시작될 때까지 대기
sleep 2

# 데이터베이스 마이그레이션 실행
echo "[INFO] Running database migrations..."
python3 manage.py migrate --noinput || echo "[WARNING] Migration failed but continuing"

# 정적 파일 수집
echo "[INFO] Collecting static files..."
python3 manage.py collectstatic --noinput || echo "[WARNING] Collectstatic failed but continuing"

# 헬스체크 서버 종료
echo "[INFO] Stopping health check server..."
kill $HEALTH_PID 2>/dev/null || true

# Gunicorn으로 실제 Django 서버 시작
echo "[INFO] Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -