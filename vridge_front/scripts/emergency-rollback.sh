#!/bin/bash

# Vercel 긴급 롤백 스크립트
# 사용법: ./emergency-rollback.sh [deployment-id]

set -e

echo "🚨 VERCEL EMERGENCY ROLLBACK SCRIPT"
echo "===================================="

# Vercel CLI 확인
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm i -g vercel
fi

# 환경 변수 확인
if [ -z "$VERCEL_TOKEN" ]; then
    echo "⚠️  VERCEL_TOKEN not set. Please login with 'vercel login'"
fi

# 최근 배포 목록 조회
echo ""
echo "📋 Recent deployments:"
vercel list --prod --limit 5

echo ""
echo "🔄 Rolling back deployment..."

if [ -z "$1" ]; then
    # 배포 ID가 제공되지 않은 경우, 이전 성공한 배포로 롤백
    echo "No deployment ID provided. Rolling back to previous successful deployment..."
    
    # 마지막 성공한 배포 찾기
    LAST_GOOD_DEPLOYMENT=$(vercel list --prod --limit 10 | grep "Ready" | head -2 | tail -1 | awk '{print $1}')
    
    if [ -z "$LAST_GOOD_DEPLOYMENT" ]; then
        echo "❌ No previous successful deployment found!"
        exit 1
    fi
    
    echo "Found last successful deployment: $LAST_GOOD_DEPLOYMENT"
    vercel rollback $LAST_GOOD_DEPLOYMENT --yes
else
    # 특정 배포 ID로 롤백
    echo "Rolling back to deployment: $1"
    vercel rollback $1 --yes
fi

echo ""
echo "✅ Rollback completed!"
echo ""
echo "📊 Post-rollback checklist:"
echo "1. Check the production site: https://your-domain.vercel.app"
echo "2. Monitor error logs: vercel logs --follow"
echo "3. Verify critical features are working"
echo "4. Update team about the rollback"

# 헬스 체크 (옵션)
if [ "$2" = "--health-check" ]; then
    echo ""
    echo "🏥 Running health check..."
    
    PROD_URL="https://your-domain.vercel.app"
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $PROD_URL)
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ Site is responding normally (HTTP $HTTP_STATUS)"
    else
        echo "⚠️  Site returned HTTP $HTTP_STATUS"
    fi
fi

echo ""
echo "📝 Don't forget to:"
echo "- Investigate the root cause of the deployment failure"
echo "- Update VERCEL_DEPLOYMENT_CHECKLIST.md if needed"
echo "- Add tests to prevent similar issues"