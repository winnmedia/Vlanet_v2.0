#!/bin/bash

echo "=========================================="
echo "Railway 자동 수정 스크립트"
echo "=========================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Railway CLI 확인
echo "1. Railway CLI 확인..."
if command -v railway &> /dev/null; then
    echo -e "${GREEN}✓ Railway CLI 설치됨 ($(railway --version))${NC}"
else
    echo -e "${RED}✗ Railway CLI가 설치되지 않았습니다.${NC}"
    echo "설치 명령어: curl -fsSL https://railway.app/install.sh | sh"
    exit 1
fi

# 2. 작업 디렉토리로 이동
echo ""
echo "2. 작업 디렉토리로 이동..."
cd /home/winnmedia/VideoPlanet/vridge_back
echo -e "${GREEN}✓ $(pwd)${NC}"

# 3. Railway 로그인 확인
echo ""
echo "3. Railway 로그인 확인..."
if railway status &> /dev/null; then
    echo -e "${GREEN}✓ 로그인됨${NC}"
else
    echo -e "${YELLOW}⚠ Railway 로그인이 필요합니다${NC}"
    echo "실행 명령어: railway login"
    echo "브라우저가 열리면 로그인 후 다시 이 스크립트를 실행하세요."
    railway login
    exit 0
fi

# 4. 데이터베이스 수정 스크립트 실행
echo ""
echo "4. 데이터베이스 수정 스크립트 실행..."
echo -e "${YELLOW}railway run python fix_railway_db.py${NC}"
railway run python fix_railway_db.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 데이터베이스 수정 완료${NC}"
else
    echo -e "${RED}✗ 데이터베이스 수정 실패${NC}"
    echo "대체 명령어 시도..."
    railway run python manage.py migrate users --fake
fi

# 5. 서비스 재시작
echo ""
echo "5. Railway 서비스 재시작..."
echo -e "${YELLOW}railway restart${NC}"
railway restart

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 서비스 재시작 완료${NC}"
else
    echo -e "${RED}✗ 재시작 실패${NC}"
fi

# 6. 로그 확인 (5초간)
echo ""
echo "6. 최근 로그 확인..."
echo -e "${YELLOW}railway logs --lines 20${NC}"
railway logs --lines 20

echo ""
echo "=========================================="
echo "수정 작업 완료!"
echo "=========================================="
echo ""
echo "테스트 명령어:"
echo "1. API 헬스체크:"
echo "   curl https://videoplanet.up.railway.app/api/health/"
echo ""
echo "2. CORS 테스트:"
echo "   curl -I -X OPTIONS \\"
echo "     -H \"Origin: https://vlanet-v2-0-krye028sg-vlanets-projects.vercel.app\" \\"
echo "     https://videoplanet.up.railway.app/api/users/login/"
echo ""
echo "3. 로그인 테스트:"
echo "   curl -X POST https://videoplanet.up.railway.app/api/users/login/ \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"email\":\"test@example.com\",\"password\":\"test123\"}'"