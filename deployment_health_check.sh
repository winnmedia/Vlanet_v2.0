#!/bin/bash

echo "==========================================="
echo "  VideoPlanet Deployment Health Check"
echo "==========================================="
echo "Date: $(date)"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backend URL
BACKEND_URL="https://videoplanet.up.railway.app"
# Frontend URL  
FRONTEND_URL="https://vlanet.net"

echo "🔍 Checking Backend (Railway)..."
echo "-------------------------------------------"

# 1. Basic health check
echo -n "1. Health Check (/): "
if curl -s "$BACKEND_URL/" | grep -q "OK"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# 2. Django status
echo -n "2. Django Status (/django-status): "
DJANGO_STATUS=$(curl -s "$BACKEND_URL/django-status" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'UNKNOWN'))" 2>/dev/null || echo "ERROR")
if [ "$DJANGO_STATUS" = "RUNNING" ]; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${RED}❌ $DJANGO_STATUS${NC}"
fi

# 3. API health
echo -n "3. API Health (/api/health/): "
if curl -s "$BACKEND_URL/api/health/" | grep -q "ok"; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

# 4. API version
echo -n "4. API Version (/api/version/): "
VERSION=$(curl -s "$BACKEND_URL/api/version/" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('version', 'UNKNOWN'))" 2>/dev/null || echo "ERROR")
if [ "$VERSION" != "ERROR" ] && [ "$VERSION" != "UNKNOWN" ]; then
    echo -e "${GREEN}✅ $VERSION${NC}"
else
    echo -e "${RED}❌ FAIL${NC}"
fi

echo ""
echo "🔍 Checking Frontend (Vercel)..."
echo "-------------------------------------------"

# 1. Frontend status
echo -n "1. Frontend Status: "
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/")
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "401" ]; then
    echo -e "${GREEN}✅ HTTP $HTTP_STATUS${NC}"
else
    echo -e "${RED}❌ HTTP $HTTP_STATUS${NC}"
fi

# 2. Check specific pages
PAGES=("/login" "/signup" "/dashboard" "/analytics" "/teams" "/settings")
echo "2. Page Checks:"
for page in "${PAGES[@]}"; do
    echo -n "   $page: "
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL$page")
    if [ "$STATUS" = "200" ] || [ "$STATUS" = "401" ]; then
        echo -e "${GREEN}✅ HTTP $STATUS${NC}"
    elif [ "$STATUS" = "404" ]; then
        echo -e "${RED}❌ 404 NOT FOUND${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTP $STATUS${NC}"
    fi
done

echo ""
echo "🔍 Checking API Integration..."
echo "-------------------------------------------"

# Test CORS
echo -n "1. CORS Preflight: "
CORS_RESPONSE=$(curl -s -X OPTIONS "$BACKEND_URL/api/auth/login/" \
    -H "Origin: $FRONTEND_URL" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" \
    -o /dev/null -w "%{http_code}")
if [ "$CORS_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
else
    echo -e "${RED}❌ FAIL (HTTP $CORS_RESPONSE)${NC}"
fi

# Test authentication endpoint
echo -n "2. Auth Endpoint (/api/auth/login/): "
AUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/auth/login/")
if [ "$AUTH_STATUS" = "405" ] || [ "$AUTH_STATUS" = "400" ]; then
    echo -e "${GREEN}✅ Reachable${NC}"
else
    echo -e "${RED}❌ HTTP $AUTH_STATUS${NC}"
fi

echo ""
echo "🔍 Performance Metrics..."
echo "-------------------------------------------"

# Backend response time
echo -n "1. Backend Response Time: "
BACKEND_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$BACKEND_URL/api/health/")
BACKEND_MS=$(echo "$BACKEND_TIME * 1000" | bc | cut -d. -f1)
if [ "$BACKEND_MS" -lt 200 ]; then
    echo -e "${GREEN}✅ ${BACKEND_MS}ms${NC}"
elif [ "$BACKEND_MS" -lt 500 ]; then
    echo -e "${YELLOW}⚠️  ${BACKEND_MS}ms${NC}"
else
    echo -e "${RED}❌ ${BACKEND_MS}ms${NC}"
fi

# Frontend response time
echo -n "2. Frontend Response Time: "
FRONTEND_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$FRONTEND_URL/")
FRONTEND_MS=$(echo "$FRONTEND_TIME * 1000" | bc | cut -d. -f1)
if [ "$FRONTEND_MS" -lt 200 ]; then
    echo -e "${GREEN}✅ ${FRONTEND_MS}ms${NC}"
elif [ "$FRONTEND_MS" -lt 500 ]; then
    echo -e "${YELLOW}⚠️  ${FRONTEND_MS}ms${NC}"
else
    echo -e "${RED}❌ ${FRONTEND_MS}ms${NC}"
fi

echo ""
echo "==========================================="
echo "  Summary"
echo "==========================================="

# Count results
BACKEND_OK=$(curl -s "$BACKEND_URL/" | grep -q "OK" && echo "1" || echo "0")
DJANGO_OK=$([ "$DJANGO_STATUS" = "RUNNING" ] && echo "1" || echo "0")
API_OK=$(curl -s "$BACKEND_URL/api/health/" | grep -q "ok" && echo "1" || echo "0")
FRONTEND_OK=$([ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "401" ] && echo "1" || echo "0")

if [ "$BACKEND_OK" = "1" ] && [ "$DJANGO_OK" = "1" ] && [ "$API_OK" = "1" ] && [ "$FRONTEND_OK" = "1" ]; then
    echo -e "${GREEN}✅ All systems operational!${NC}"
    echo "Backend: Running ✅"
    echo "Frontend: Running ✅"
    echo "API: Healthy ✅"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some issues detected${NC}"
    [ "$BACKEND_OK" = "0" ] && echo "Backend: Issues detected ⚠️"
    [ "$DJANGO_OK" = "0" ] && echo "Django: Not running properly ⚠️"
    [ "$API_OK" = "0" ] && echo "API: Health check failed ⚠️"
    [ "$FRONTEND_OK" = "0" ] && echo "Frontend: Issues detected ⚠️"
    exit 1
fi