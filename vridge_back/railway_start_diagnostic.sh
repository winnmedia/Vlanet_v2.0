#!/bin/bash
# Railway Diagnostic Startup Script
# 극도로 상세한 진단 정보를 제공

set -e  # 에러 발생 시 즉시 중단

echo "=========================================="
echo "Railway Diagnostic Server Starting"
echo "Time: $(date)"
echo "=========================================="

# 환경 정보 출력
echo ""
echo "=== ENVIRONMENT INFO ==="
echo "PORT: ${PORT:-NOT_SET}"
echo "RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-NOT_SET}"
echo "RAILWAY_SERVICE_ID: ${RAILWAY_SERVICE_ID:-NOT_SET}"
echo "PWD: $(pwd)"
echo "USER: $(whoami)"
echo "HOME: $HOME"

# Python 정보
echo ""
echo "=== PYTHON INFO ==="
which python || echo "python not found"
which python3 || echo "python3 not found"
python --version 2>&1 || python3 --version 2>&1
echo "Python path: $(which python3 || which python)"

# 디렉토리 구조
echo ""
echo "=== DIRECTORY STRUCTURE ==="
echo "Current directory contents:"
ls -la | head -20

echo ""
echo "Looking for important files:"
[ -f "manage.py" ] && echo "✓ manage.py found" || echo "✗ manage.py NOT FOUND"
[ -f "railway_diagnostic.py" ] && echo "✓ railway_diagnostic.py found" || echo "✗ railway_diagnostic.py NOT FOUND"
[ -f "requirements.txt" ] && echo "✓ requirements.txt found" || echo "✗ requirements.txt NOT FOUND"
[ -d "vridge_back" ] && echo "✓ vridge_back/ directory found" || echo "✗ vridge_back/ directory NOT FOUND"

# Python 패키지 확인
echo ""
echo "=== PYTHON PACKAGES ==="
pip list | grep -E "django|gunicorn|psycopg2|whitenoise" || echo "Core packages check failed"

# 진단 서버 시작
echo ""
echo "=== STARTING DIAGNOSTIC SERVER ==="
echo "Using PORT: ${PORT:-8000}"

# gunicorn으로 진단 서버 실행
exec gunicorn railway_diagnostic:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 1 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance \
    --preload