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

# CORS 관련 환경 변수 강제 설정
export CORS_ALLOW_CREDENTIALS=true
export CORS_ALLOWED_ORIGINS="https://vlanet.net,https://www.vlanet.net"

echo "[INFO] 환경 변수 설정 완료"
echo "  - DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo "  - PORT: $PORT"
echo "  - DATABASE_URL: ${DATABASE_URL:0:30}..."
echo "  - CORS_ALLOW_CREDENTIALS: $CORS_ALLOW_CREDENTIALS"

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

# 3. 향상된 데이터베이스 연결 테스트
echo "[STEP 3/6] 데이터베이스 연결 테스트 및 검증..."
python3 -c "
import os
import sys
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
import django
django.setup()

from django.db import connection

# Railway PostgreSQL 연결 테스트
max_retries = 5
retry_delay = 2

for attempt in range(max_retries):
    try:
        print(f'[ATTEMPT {attempt + 1}/{max_retries}] 데이터베이스 연결 시도...')
        
        # 기존 연결 닫기 (새 연결 강제)
        if connection.connection:
            connection.close()
        
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute('SELECT version(), current_database(), current_user')
            result = cursor.fetchone()
            connection_time = (time.time() - start_time) * 1000
            
        print(f'[SUCCESS] PostgreSQL 연결 성공 ({connection_time:.2f}ms)')
        print(f'  - Version: {result[0][:50]}...')
        print(f'  - Database: {result[1]}')
        print(f'  - User: {result[2]}')
        
        # users 테이블 확인
        try:
            cursor.execute('SELECT COUNT(*) FROM users_user')
            user_count = cursor.fetchone()[0]
            print(f'  - Users count: {user_count}')
        except Exception as e:
            print(f'  - Users table check failed: {e}')
        
        break
        
    except Exception as e:
        print(f'[ERROR] 연결 실패 (시도 {attempt + 1}/{max_retries}): {e}')
        if attempt < max_retries - 1:
            print(f'[INFO] {retry_delay}초 후 재시도...')
            time.sleep(retry_delay)
            retry_delay *= 1.5  # 지수 백오프
        else:
            print('[CRITICAL] 모든 연결 시도 실패')
            print('[INFO] 서비스는 계속 시작하지만 로그인 문제가 발생할 수 있습니다')
"

# 4. 마이그레이션 실행
echo "[STEP 4/6] 데이터베이스 마이그레이션..."
python3 manage.py migrate --noinput 2>&1 | head -50 || {
    echo "[WARNING] 마이그레이션 일부 실패, 계속 진행"
}

# 4.1. Demo 사용자 생성 (Railway 전용)
echo "[STEP 4.1/6] Demo 사용자 생성/검증..."
python3 create_railway_demo_user.py 2>&1 | head -30 || {
    echo "[WARNING] Demo 사용자 생성 실패, 계속 진행"
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

# Gunicorn 실행 (최적화된 설정 + CORS 헤더 보장)
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
    --preload \
    --forwarded-allow-ips="*" \
    --proxy-protocol \
    --proxy-allow-from="*"