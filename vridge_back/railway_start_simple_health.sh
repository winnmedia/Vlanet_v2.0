#!/bin/bash
# Railway Simple Health Check Startup
# 극도로 단순한 헬스체크 전용 시작 스크립트

echo "=========================================="
echo "Railway Simple Health Server"
echo "Time: $(date)"
echo "=========================================="

# 기본 정보만 출력
echo "PORT: ${PORT:-8000}"
echo "PWD: $(pwd)"
echo "Python: $(which python3 || which python)"

# 디렉토리 내용 확인
echo ""
echo "Directory contents:"
ls -la | grep -E "\.py$|requirements" | head -10

# gunicorn으로 간단한 헬스체크 서버 실행
echo ""
echo "Starting health check server on port ${PORT:-8000}..."

exec gunicorn railway_simple_health:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 1 \
    --timeout 30 \
    --log-level info \
    --access-logfile - \
    --error-logfile -