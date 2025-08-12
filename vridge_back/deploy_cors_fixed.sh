#!/bin/bash

# CORS Fix Deployment Verification Script
# This script verifies the CORS fix has been properly applied

echo "========================================="
echo "CORS Fix Deployment Verification"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check file content
check_file() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        return 0
    else
        echo -e "${RED}✗${NC} $description"
        return 1
    fi
}

echo "1. Checking Configuration Files:"
echo "---------------------------------"

# Check Procfile
check_file "Procfile" "gunicorn config.wsgi:application" "Procfile uses Gunicorn"

# Check railway.json
check_file "railway.json" "gunicorn config.wsgi:application" "railway.json uses Gunicorn"
check_file "railway.json" "RAILWAY_ENVIRONMENT" "railway.json sets RAILWAY_ENVIRONMENT"

# Check requirements.txt
check_file "requirements.txt" "django-cors-headers" "django-cors-headers in requirements.txt"
check_file "requirements.txt" "gunicorn" "gunicorn in requirements.txt"

echo ""
echo "2. Checking Django Settings:"
echo "-----------------------------"

# Check if settings file exists
if [ -f "config/settings/railway.py" ]; then
    echo -e "${GREEN}✓${NC} Railway settings file exists"
    
    # Check CORS configuration
    check_file "config/settings/railway.py" "CORS_ALLOWED_ORIGINS" "CORS_ALLOWED_ORIGINS configured"
    check_file "config/settings/railway.py" "https://vlanet.net" "vlanet.net in CORS_ALLOWED_ORIGINS"
    check_file "config/settings/railway.py" "https://www.vlanet.net" "www.vlanet.net in CORS_ALLOWED_ORIGINS"
    check_file "config/settings/railway.py" "corsheaders" "corsheaders in INSTALLED_APPS or imported"
else
    echo -e "${RED}✗${NC} Railway settings file missing"
fi

echo ""
echo "3. Testing Local Server (if running):"
echo "--------------------------------------"

# Test if server is running on port 8000
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health/ | grep -q "200"; then
    echo -e "${GREEN}✓${NC} Server is running on port 8000"
    
    # Test CORS headers
    CORS_HEADER=$(curl -s -I -H 'Origin: https://vlanet.net' http://localhost:8000/api/health/ | grep -i "access-control-allow-origin")
    if echo "$CORS_HEADER" | grep -q "https://vlanet.net"; then
        echo -e "${GREEN}✓${NC} CORS headers working for vlanet.net"
    else
        echo -e "${RED}✗${NC} CORS headers not working for vlanet.net"
    fi
    
    # Test preflight
    OPTIONS_RESPONSE=$(curl -s -X OPTIONS -I -H 'Origin: https://vlanet.net' -H 'Access-Control-Request-Method: POST' http://localhost:8000/api/health/ | grep -i "access-control-allow-methods")
    if echo "$OPTIONS_RESPONSE" | grep -q "POST"; then
        echo -e "${GREEN}✓${NC} Preflight OPTIONS requests working"
    else
        echo -e "${RED}✗${NC} Preflight OPTIONS requests not working"
    fi
else
    echo -e "${YELLOW}⚠${NC} Server not running on port 8000 (test skipped)"
fi

echo ""
echo "========================================="
echo "Deployment Checklist:"
echo "========================================="
echo ""
echo "[ ] All configuration checks passed above"
echo "[ ] Commit these files to git:"
echo "    - Procfile"
echo "    - railway.json"
echo "    - config/settings/railway.py"
echo "    - config/wsgi.py"
echo "    - gunicorn_config.py"
echo "    - users/views_api.py (swagger decorators commented)"
echo ""
echo "[ ] Push to Railway deployment branch:"
echo "    git add ."
echo "    git commit -m 'fix: Switch to Gunicorn for proper CORS handling'"
echo "    git push origin main"
echo ""
echo "[ ] Monitor Railway deployment logs:"
echo "    - Check for successful Gunicorn startup"
echo "    - Verify no import errors"
echo "    - Confirm health check passes"
echo ""
echo "[ ] Test from frontend after deployment:"
echo "    1. Open https://vlanet.net in browser"
echo "    2. Open DevTools Network tab"
echo "    3. Try to login or make API call"
echo "    4. Verify no CORS errors in console"
echo "    5. Check response headers include Access-Control-Allow-Origin"
echo ""
echo "[ ] Rollback command if needed:"
echo "    git revert HEAD"
echo "    git push origin main"
echo ""
echo "========================================="
echo "Script completed!"
echo "========================================="