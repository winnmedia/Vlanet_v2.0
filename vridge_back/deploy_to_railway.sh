#!/bin/bash
# Railway 배포 전 검증 및 배포 스크립트

echo "=========================================="
echo "Railway Deployment Verification Script"
echo "=========================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 결과 저장 변수
ERRORS=0
WARNINGS=0

# 함수: 성공 메시지
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# 함수: 경고 메시지
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# 함수: 에러 메시지
error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

echo ""
echo "1. 환경 체크"
echo "----------------------------------------"

# Python 버전 체크
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ $PYTHON_VERSION == 3.* ]]; then
    success "Python version: $PYTHON_VERSION"
else
    error "Python 3 is required"
fi

# Django 설치 확인
if python3 -c "import django" 2>/dev/null; then
    DJANGO_VERSION=$(python3 -c "import django; print(django.get_version())")
    success "Django version: $DJANGO_VERSION"
else
    error "Django is not installed"
fi

echo ""
echo "2. 파일 존재 확인"
echo "----------------------------------------"

# 필수 파일 체크
FILES=(
    "manage.py"
    "config/wsgi.py"
    "config/settings/railway.py"
    "railway_start.sh"
    "railway_health.py"
    "railway.json"
    "requirements.txt"
    "users/railway_auth.py"
    "config/auth_fallback.py"
)

for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        success "$file exists"
    else
        error "$file not found"
    fi
done

echo ""
echo "3. Railway 설정 검증"
echo "----------------------------------------"

# railway.json 검증
if [[ -f "railway.json" ]]; then
    if python3 -c "import json; json.load(open('railway.json'))" 2>/dev/null; then
        success "railway.json is valid JSON"
        
        # build 명령 확인
        BUILD_CMD=$(python3 -c "import json; print(json.load(open('railway.json')).get('build', {}).get('builder', 'not found'))")
        echo "  Builder: $BUILD_CMD"
        
        # start 명령 확인
        START_CMD=$(python3 -c "import json; print(json.load(open('railway.json')).get('deploy', {}).get('startCommand', 'not found'))")
        echo "  Start command: $START_CMD"
    else
        error "railway.json is not valid JSON"
    fi
fi

echo ""
echo "4. 인증 시스템 테스트"
echo "----------------------------------------"

# Railway 환경 시뮬레이션
export RAILWAY_ENVIRONMENT=production
export DJANGO_SETTINGS_MODULE=config.settings.railway

python3 -c "
import os
import django
try:
    django.setup()
    from config.auth_fallback import get_auth_views
    views = get_auth_views()
    if views['login'].__name__ == 'RailwayLogin':
        print('✓ Railway auth views loaded correctly')
    else:
        print('✗ Wrong auth view loaded:', views['login'].__name__)
except Exception as e:
    print('✗ Auth system error:', e)
" 2>&1 | while IFS= read -r line; do
    if [[ $line == *"✓"* ]]; then
        success "${line#*✓ }"
    elif [[ $line == *"✗"* ]]; then
        error "${line#*✗ }"
    else
        echo "  $line"
    fi
done

# 환경 변수 초기화
unset RAILWAY_ENVIRONMENT
unset DJANGO_SETTINGS_MODULE

echo ""
echo "5. 데이터베이스 마이그레이션 확인"
echo "----------------------------------------"

# 마이그레이션 상태 체크
python3 manage.py showmigrations --list 2>/dev/null | head -5
if [[ $? -eq 0 ]]; then
    success "Migrations are accessible"
else
    warning "Could not check migrations (database may not be configured)"
fi

echo ""
echo "6. 정적 파일 설정 확인"
echo "----------------------------------------"

# STATIC_ROOT 확인
STATIC_ROOT=$(python3 -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.railway'
import django
django.setup()
from django.conf import settings
print(settings.STATIC_ROOT)
" 2>/dev/null)

if [[ -n "$STATIC_ROOT" ]]; then
    success "STATIC_ROOT configured: $STATIC_ROOT"
else
    error "STATIC_ROOT not configured"
fi

echo ""
echo "7. 권한 확인"
echo "----------------------------------------"

# 실행 권한 체크
if [[ -x "railway_start.sh" ]]; then
    success "railway_start.sh is executable"
else
    warning "railway_start.sh is not executable, fixing..."
    chmod +x railway_start.sh
    success "railway_start.sh made executable"
fi

echo ""
echo "=========================================="
echo "검증 결과"
echo "=========================================="
echo -e "Errors: ${RED}$ERRORS${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    echo -e "${RED}배포 전 해결해야 할 문제가 있습니다.${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}모든 검증을 통과했습니다!${NC}"
    echo ""
    echo "Railway 배포 방법:"
    echo "1. git add ."
    echo "2. git commit -m 'Fix Railway authentication and deployment'"
    echo "3. git push origin main"
    echo "4. Railway 대시보드에서 배포 상태 확인"
    echo ""
    echo "또는 Railway CLI 사용:"
    echo "1. railway login"
    echo "2. railway up"
    echo ""
    
    if [[ $WARNINGS -gt 0 ]]; then
        echo -e "${YELLOW}경고 사항이 있지만 배포는 가능합니다.${NC}"
    fi
fi