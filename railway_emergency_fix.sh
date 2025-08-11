#!/bin/bash

echo "=========================================="
echo "Railway 긴급 복구 스크립트"
echo "=========================================="
echo ""
echo "이 스크립트는 Railway 토큰을 사용하여 실행합니다."
echo ""

# Railway 토큰 확인
if [ -z "$RAILWAY_TOKEN" ]; then
    echo "❌ RAILWAY_TOKEN이 설정되지 않았습니다."
    echo ""
    echo "설정 방법:"
    echo "1. https://railway.app/account/tokens 접속"
    echo "2. 'Create Token' 클릭"
    echo "3. 토큰 복사"
    echo "4. export RAILWAY_TOKEN='복사한_토큰'"
    echo "5. 이 스크립트 재실행"
    exit 1
fi

echo "✅ Railway 토큰 확인됨"
echo ""

# 작업 디렉토리
cd /home/winnmedia/VideoPlanet/vridge_back

# 1. 서비스 재시작 시도
echo "1. Railway 서비스 재시작..."
railway restart 2>/dev/null || echo "⚠️  재시작 실패 - Railway 웹 콘솔에서 수동 재시작 필요"

# 2. 환경 변수 설정
echo ""
echo "2. 환경 변수 설정..."
cat << 'EOF'
railway variables set DJANGO_SETTINGS_MODULE=config.settings.railway
railway variables set DEBUG=False
railway variables set CORS_ALLOWED_ORIGINS="https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app,https://vlanet.net"
EOF

# 3. 데이터베이스 수정 명령어
echo ""
echo "3. 데이터베이스 수정 명령어:"
echo "railway run python fix_railway_db.py"
echo ""
echo "또는:"
echo ""
cat << 'EOF'
railway run python manage.py shell << SCRIPT
from django.db import connection
with connection.cursor() as cursor:
    try:
        cursor.execute("ALTER TABLE users_user ALTER COLUMN deletion_reason SET DEFAULT ''")
        cursor.execute("UPDATE users_user SET deletion_reason = '' WHERE deletion_reason IS NULL")
        print("✅ Fixed!")
    except Exception as e:
        print(f"Error: {e}")
SCRIPT
EOF

echo ""
echo "=========================================="
echo "Railway 웹 콘솔 대체 방법"
echo "=========================================="
echo ""
echo "1. https://railway.app 접속"
echo "2. VideoPlane 프로젝트 선택"
echo "3. Deploy 탭 → Restart 클릭"
echo "4. Variables 탭에서 환경 변수 확인"
echo "5. Observability → Logs에서 에러 확인"
echo ""
echo "=========================================="