#!/bin/bash
# Railway 시작 스크립트

echo "=== Railway 시작 스크립트 실행 ==="
echo "PORT: $PORT"
echo "PWD: $(pwd)"
echo "Python: $(which python3)"
echo "Gunicorn: $(which gunicorn)"

# 파일 존재 확인
echo "=== 파일 확인 ==="
ls -la simple_health.py 2>/dev/null || echo "simple_health.py 없음"
ls -la health_server.py 2>/dev/null || echo "health_server.py 없음"
ls -la basic_health.py 2>/dev/null || echo "basic_health.py 없음"

# 가장 간단한 헬스체크 서버 실행
if [ -f "basic_health.py" ]; then
    echo "basic_health.py 실행"
    python3 basic_health.py
elif [ -f "simple_health.py" ]; then
    echo "simple_health.py with gunicorn 실행"
    gunicorn simple_health:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
else
    echo "헬스체크 파일 없음, 기본 gunicorn 실행"
    gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120
fi