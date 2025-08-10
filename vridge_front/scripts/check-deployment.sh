#!/bin/bash

echo "======================================"
echo "VideoPlanet Deployment Health Check"
echo "======================================"
echo ""

# Check DNS
echo "1. DNS 확인:"
echo "   vlanet.net DNS 레코드:"
dig +short vlanet.net
echo ""

# Check current deployment
echo "2. 현재 배포 상태:"
curl -s -I https://vlanet.net | head -n 5
echo ""

# Check API connectivity
echo "3. API 연결 확인:"
curl -s -o /dev/null -w "   Railway API 응답 코드: %{http_code}\n" https://videoplanet.up.railway.app/health
echo ""

# Check Vercel deployment
echo "4. Vercel 프로젝트 정보:"
if command -v vercel &> /dev/null; then
    vercel whoami 2>/dev/null || echo "   Vercel CLI 로그인 필요"
    echo ""
    echo "   최근 배포:"
    vercel ls --limit 3 2>/dev/null || echo "   배포 정보 없음"
else
    echo "   Vercel CLI가 설치되지 않음"
fi
echo ""

echo "======================================"
echo "문제 해결 체크리스트:"
echo "======================================"
echo "[ ] 1. vercel.json에 NEXT_PUBLIC_API_URL 설정됨"
echo "[ ] 2. .env.production 파일 생성됨"
echo "[ ] 3. vlanet.net이 올바른 Vercel 프로젝트에 연결됨"
echo "[ ] 4. Railway 백엔드가 실행 중"
echo "[ ] 5. 최신 코드가 main 브랜치에 푸시됨"
echo ""