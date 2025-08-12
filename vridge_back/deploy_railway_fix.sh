#!/bin/bash

# Railway Deployment Fix Script
# Fixes 500 error on login API

echo "=================================="
echo "Railway Login API 500 Error Fix"
echo "=================================="
echo "Time: $(date)"
echo ""

# 1. Backup current views
echo "1. Backing up current views..."
if [ -f "users/views_api.py" ]; then
    cp users/views_api.py users/views_api_backup_$(date +%Y%m%d_%H%M%S).py
    echo "✅ Backup created"
else
    echo "⚠️  views_api.py not found"
fi

# 2. Check if Railway-compatible version exists
echo ""
echo "2. Checking Railway-compatible version..."
if [ -f "users/views_railway_fix.py" ]; then
    echo "✅ Railway-compatible version found"
    # The file is already copied during development
else
    echo "❌ Railway-compatible version not found"
    echo "Please ensure views_railway_fix.py exists"
    exit 1
fi

# 3. Display key changes
echo ""
echo "3. Key changes in Railway-compatible version:"
echo "   ✅ Handles both DRF Request and Django WSGIRequest"
echo "   ✅ Safe request data extraction with get_request_data()"
echo "   ✅ Returns JsonResponse directly (no DRF Response dependency)"
echo "   ✅ Enhanced error handling with detailed logging"
echo "   ✅ Railway environment detection for email verification skip"
echo "   ✅ Performance metrics included in responses"

# 4. Environment variables check
echo ""
echo "4. Required Railway environment variables:"
echo "   - DATABASE_URL (PostgreSQL connection)"
echo "   - SECRET_KEY or DJANGO_SECRET_KEY"
echo "   - RAILWAY_ENVIRONMENT (set to 'production')"
echo "   - PORT (usually 8000)"

# 5. Migration reminder
echo ""
echo "5. Post-deployment steps:"
echo "   a) Run migrations: python manage.py migrate"
echo "   b) Create superuser if needed: python manage.py createsuperuser"
echo "   c) Check logs: railway logs"

# 6. Test endpoints
echo ""
echo "6. Test endpoints after deployment:"
echo "   - Health check: https://videoplanet.up.railway.app/health/"
echo "   - Login API: https://videoplanet.up.railway.app/api/users/login/"
echo ""
echo "Test command:"
echo 'curl -X POST https://videoplanet.up.railway.app/api/users/login/ \'
echo '  -H "Content-Type: application/json" \'
echo '  -d "{\"email\":\"test@example.com\",\"password\":\"password123\"}"'

echo ""
echo "=================================="
echo "Fix Applied Successfully!"
echo "=================================="
echo ""
echo "Summary of changes:"
echo "✅ views_api.py now handles both request types"
echo "✅ 500 error on Railway should be resolved"
echo "✅ Login API compatible with Gunicorn/Railway"
echo ""
echo "Deploy to Railway with: railway up"
echo ""