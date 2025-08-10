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

# 데이터베이스 연결 확인 (재시도 로직)
log_info "데이터베이스 연결 확인 중..."
for i in {1..5}; do
    if python manage.py check --database default; then
        log_info "데이터베이스 연결 성공!"
        break
    else
        log_error "데이터베이스 연결 실패 ($i/5). 5초 후 재시도..."
        sleep 5
    fi
    
    if [ $i -eq 5 ]; then
        log_error "데이터베이스 연결에 실패했습니다."
        exit 1
    fi
done

# 마이그레이션 상태 확인
log_info "마이그레이션 상태 확인 중..."
python manage.py showmigrations --verbosity=1

# 미적용 마이그레이션 확인 및 실행
log_info "미적용 마이그레이션 확인 중..."
if python manage.py showmigrations --plan | grep -q '\[ \]'; then
    log_info "미적용 마이그레이션 발견. 실행 중..."
    python manage.py migrate --verbosity=2 --noinput
    log_info "마이그레이션 완료!"
else
    log_info "모든 마이그레이션이 이미 적용되었습니다."
fi

# is_deleted 필드 확인 (특별 체크)
log_info "User 모델 is_deleted 필드 확인 중..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT is_deleted FROM users_user LIMIT 1')
    print('[INFO] is_deleted 필드 확인 완료!')
except Exception as e:
    print(f'[ERROR] is_deleted 필드 오류: {e}')
    raise
"

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

log_info "Gunicorn 서버 시작..."
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