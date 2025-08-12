#!/bin/bash

# CORS Fix Deployment Script for Railway
# This script applies the architectural fix for CORS issues

echo "========================================="
echo "CORS Architecture Fix Deployment"
echo "========================================="

# Step 1: Backup current configuration
echo "Step 1: Backing up current configuration..."
cp Procfile Procfile.backup_$(date +%Y%m%d_%H%M%S)
cp railway.json railway.json.backup_$(date +%Y%m%d_%H%M%S)
cp config/settings/railway.py config/settings/railway.py.backup_$(date +%Y%m%d_%H%M%S)

# Step 2: Apply new configuration
echo "Step 2: Applying new configuration..."
cp Procfile_fixed Procfile
echo "✓ Procfile updated to use Gunicorn instead of cors_server.py"

# Step 3: Update railway.json
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --access-logfile - --error-logfile -",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "healthcheckPath": "/api/health/",
    "healthcheckTimeout": 30,
    "replicas": 1
  },
  "environments": {
    "production": {
      "variables": {
        "DJANGO_SETTINGS_MODULE": "config.settings.railway_fixed",
        "PYTHONPATH": "/app",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
EOF
echo "✓ railway.json updated"

# Step 4: Update settings import in wsgi.py
sed -i 's/config.settings.railway/config.settings.railway_fixed/g' config/wsgi.py
echo "✓ wsgi.py updated to use fixed settings"

# Step 5: Ensure gunicorn is in requirements.txt
if ! grep -q "gunicorn" requirements.txt; then
    echo "gunicorn==21.2.0" >> requirements.txt
    echo "✓ Added gunicorn to requirements.txt"
fi

# Step 6: Ensure django-cors-headers is in requirements.txt
if ! grep -q "django-cors-headers" requirements.txt; then
    echo "django-cors-headers==4.3.1" >> requirements.txt
    echo "✓ Added django-cors-headers to requirements.txt"
fi

# Step 7: Create health check endpoint if not exists
cat > config/health_view.py << 'EOF'
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time

@csrf_exempt
def health_check(request):
    """Simple health check endpoint that always includes CORS headers"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'videoplanet-backend'
    })
EOF
echo "✓ Health check view created"

# Step 8: Verify local setup
echo ""
echo "Step 8: Testing configuration locally..."
echo "Please run the following commands to test:"
echo ""
echo "1. Install dependencies:"
echo "   pip install gunicorn django-cors-headers"
echo ""
echo "2. Test with Gunicorn:"
echo "   DJANGO_SETTINGS_MODULE=config.settings.railway_fixed gunicorn config.wsgi:application --bind 0.0.0.0:8000"
echo ""
echo "3. Test CORS headers:"
echo "   curl -I -H 'Origin: https://vlanet.net' http://localhost:8000/api/health/"
echo ""

# Step 9: Deployment checklist
echo "========================================="
echo "Deployment Checklist:"
echo "========================================="
echo "[ ] Local testing completed successfully"
echo "[ ] All tests pass with new configuration"
echo "[ ] Commit changes to git"
echo "[ ] Push to Railway deployment branch"
echo "[ ] Monitor Railway logs for startup issues"
echo "[ ] Test from frontend (https://vlanet.net)"
echo "[ ] Verify CORS headers in browser DevTools"
echo "[ ] Monitor error rates for 1 hour"
echo ""
echo "Rollback command if needed:"
echo "  git checkout HEAD -- Procfile railway.json config/wsgi.py"
echo ""
echo "========================================="
echo "Script completed. Please follow the checklist above."
echo "========================================="