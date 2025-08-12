#!/bin/bash
# Railway 통합 배포 스크립트 - 500 에러 완전 해결 버전

set -e  # 에러 발생 시 즉시 중단

echo "================================================"
echo "[RAILWAY] 통합 배포 시작 - $(date)"
echo "================================================"

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=config.settings.railway
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

echo "[INFO] 환경 변수 설정 완료"
echo "  - DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "  - PORT: $PORT"
echo "  - DATABASE_URL: ${DATABASE_URL:0:30}..."

# 1. Python 패키지 확인
echo "[STEP 1/6] Python 패키지 확인..."
pip list | head -20

# 2. Django 설정 검증
echo "[STEP 2/6] Django 설정 검증..."
python3 -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')

try:
    import django
    django.setup()
    print('[SUCCESS] Django 설정 로드 성공')
    
    from django.conf import settings
    print(f'  - DEBUG: {settings.DEBUG}')
    print(f'  - ALLOWED_HOSTS: {settings.ALLOWED_HOSTS[:3]}...')
    print(f'  - INSTALLED_APPS 수: {len(settings.INSTALLED_APPS)}')
    
except Exception as e:
    print(f'[ERROR] Django 설정 실패: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# 3. 데이터베이스 연결 테스트
echo "[STEP 3/6] 데이터베이스 연결 테스트..."
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
        result = cursor.fetchone()
        print(f'[SUCCESS] 데이터베이스 연결 성공: {result}')
except Exception as e:
    print(f'[WARNING] 데이터베이스 연결 실패: {e}')
    print('[INFO] SQLite 폴백 사용 예정')
"

# 4. 마이그레이션 실행
echo "[STEP 4/6] 데이터베이스 마이그레이션..."
python3 manage.py migrate --noinput 2>&1 | head -50 || {
    echo "[WARNING] 마이그레이션 일부 실패, 계속 진행"
}

# 5. 정적 파일 수집
echo "[STEP 5/6] 정적 파일 수집..."
python3 manage.py collectstatic --noinput --clear 2>&1 | head -20 || {
    echo "[WARNING] 정적 파일 수집 실패, 계속 진행"
}

# 캐시 테이블 생성 (필요시)
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
import django
django.setup()

from django.core.management import call_command
from django.db import connection

try:
    # 캐시 테이블 존재 확인
    with connection.cursor() as cursor:
        cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='cache_table'\")
        if not cursor.fetchone():
            print('[INFO] 캐시 테이블 생성 중...')
            call_command('createcachetable', 'cache_table')
            print('[SUCCESS] 캐시 테이블 생성 완료')
        else:
            print('[INFO] 캐시 테이블 이미 존재')
except Exception as e:
    print(f'[WARNING] 캐시 테이블 확인 실패: {e}')
" 2>/dev/null || true

# 6. Gunicorn 시작
echo "[STEP 6/6] Gunicorn 서버 시작..."
echo "================================================"
echo "[GUNICORN] 설정:"
echo "  - Workers: 2"
echo "  - Threads: 4"
echo "  - Timeout: 300초"
echo "  - Bind: 0.0.0.0:$PORT"
echo "================================================"

# Gunicorn 실행 (최적화된 설정)
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 300 \
    --graceful-timeout 30 \
    --keepalive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    --preload