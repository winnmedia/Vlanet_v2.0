#!/bin/bash

# Railway 배포를 위한 시작 스크립트
# 데이터베이스 마이그레이션과 함께 안전한 서버 시작

set -e  # 에러 발생 시 스크립트 중단

# 로깅 함수
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

log_info "=== VideoPlanet Backend 시작 ==="

# 환경 변수 확인
log_info "Django 설정: $DJANGO_SETTINGS_MODULE"
log_info "데이터베이스 URL: ${DATABASE_URL:0:20}..."
log_info "포트: $PORT"

# 강력한 데이터베이스 연결 확인 (Railway 환경 특화)
log_info "데이터베이스 연결 확인 중... (Railway 환경)"
log_info "DATABASE_URL: ${DATABASE_URL:0:30}..."

# 데이터베이스 준비를 위해 초기 대기
log_info "Railway 데이터베이스 서비스 준비 대기..."
sleep 10

for i in {1..10}; do
    if python manage.py check --database default; then
        log_info "데이터베이스 연결 성공! (시도 $i/10)"
        break
    else
        log_error "데이터베이스 연결 실패 ($i/10). 8초 후 재시도..."
        
        # 데이터베이스 상태 진단
        python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('[DB-CHECK] PostgreSQL 연결 성공')
    conn.close()
except Exception as e:
    print(f'[DB-CHECK] PostgreSQL 연결 실패: {e}')
        " 2>/dev/null || log_error "PostgreSQL 상태 진단 실패"
        
        sleep 8
    fi
    
    if [ $i -eq 10 ]; then
        log_error "데이터베이스 연결에 최종 실패했습니다. Railway 데이터베이스 서비스를 확인하세요."
        exit 1
    fi
done

# 강력한 마이그레이션 로직 - Railway 환경 특화
log_info "마이그레이션 상태 확인 중..."
python manage.py showmigrations --verbosity=1

# 무조건 마이그레이션 실행 (Railway 환경에서는 안전)
log_info "마이그레이션 강제 실행 중... (Railway 환경)"
python manage.py migrate --verbosity=2 --noinput || {
    log_error "일반 마이그레이션 실패. 개별 앱 마이그레이션 시도..."
    
    # 개별 앱별 마이그레이션 실행
    for app in "users" "projects" "video_analysis" "feedbacks" "core"; do
        log_info "$app 마이그레이션 실행 중..."
        if python manage.py migrate $app --verbosity=2 --noinput; then
            log_info "$app 마이그레이션 성공"
        else
            log_error "$app 마이그레이션 실패"
        fi
    done
}

# 마이그레이션 재확인
log_info "마이그레이션 결과 재확인..."
python manage.py showmigrations --verbosity=1

# 중요 필드 존재 여부 강력 검증
log_info "중요 데이터베이스 필드 검증 중..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()
from django.db import connection

def check_field_exists(table, field):
    try:
        cursor = connection.cursor()
        cursor.execute(f'SELECT {field} FROM {table} LIMIT 1')
        return True
    except Exception:
        return False

# 중요 필드들 검증
fields_to_check = [
    ('users_user', 'is_deleted'),
    ('users_user', 'deleted_at'),
    ('users_user', 'can_recover'),
    ('users_user', 'deletion_reason')
]

all_fields_exist = True
for table, field in fields_to_check:
    if check_field_exists(table, field):
        print(f'[INFO] {table}.{field} 필드 존재 확인!')
    else:
        print(f'[ERROR] {table}.{field} 필드 누락!')
        all_fields_exist = False

if all_fields_exist:
    print('[SUCCESS] 모든 중요 필드 검증 성공!')
else:
    print('[CRITICAL] 중요 필드 누락 발견 - 마이그레이션 문제 가능성')
    # 수동으로 is_deleted 필드 추가 (마지막 수단)
    try:
        cursor = connection.cursor()
        cursor.execute('ALTER TABLE users_user ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE')
        cursor.execute('ALTER TABLE users_user ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL')
        cursor.execute('ALTER TABLE users_user ADD COLUMN IF NOT EXISTS can_recover BOOLEAN DEFAULT TRUE')
        cursor.execute('ALTER TABLE users_user ADD COLUMN IF NOT EXISTS deletion_reason VARCHAR(200) NULL')
        cursor.execute('ALTER TABLE users_user ADD COLUMN IF NOT EXISTS recovery_deadline TIMESTAMP NULL')
        print('[RECOVERY] 수동으로 필드 추가 시도 완료')
    except Exception as e:
        print(f'[RECOVERY-ERROR] 수동 필드 추가 실패: {e}')
        raise
"

# 최종 데이터베이스 상태 검증
log_info "최종 데이터베이스 상태 검증..."
python manage.py check --database default || {
    log_error "데이터베이스 검증 실패 - 서버 시작 중단"
    exit 1
}

# 정적 파일 수집 (운영 환경에서만)
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.railway" ]; then
    log_info "정적 파일 수집 중..."
    python manage.py collectstatic --noinput --clear || {
        log_error "정적 파일 수집 실패, 계속 진행..."
    }
fi

# 서버 시작 전 최종 검증
log_info "서버 시작 전 최종 검증..."
python manage.py check --deploy --fail-level WARNING

# 서버 시작 전 최종 검증
log_info "=== 서버 시작 전 최종 검증 ==="
log_info "Django 설정: $DJANGO_SETTINGS_MODULE"
log_info "포트: $PORT"
log_info "마이그레이션 상태:"
python manage.py showmigrations users --verbosity=0 | tail -3

# Critical 필드 재검증
log_info "is_deleted 필드 재검증..."
python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()
from django.db import connection
from users.models import User
try:
    # 직접 ORM으로 테스트
    user_count = User.objects.filter(is_deleted=False).count()
    print(f'[FINAL-CHECK] User.objects.filter(is_deleted=False).count() = {user_count} (SUCCESS)')
except Exception as e:
    print(f'[FINAL-CHECK] ORM 테스트 실패: {e}')
    raise Exception('is_deleted 필드가 없거나 ORM에서 접근할 수 없습니다')
" || {
    log_error "CRITICAL: is_deleted 필드 ORM 테스트 실패 - 서버 시작 중단"
    exit 1
}

log_info "=== Gunicorn 서버 시작 ==="
log_info "Railway 환경에서 VideoPlanet Backend 시작 중..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --workers 2 \
    --threads 4 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --preload \
    --max-requests 1000 \
    --max-requests-jitter 50