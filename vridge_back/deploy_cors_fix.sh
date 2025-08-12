#!/bin/bash

# CORS Fix Deployment Script for Railway
# This script commits and deploys the CORS fixes to Railway

echo "=================================="
echo "CORS Fix Deployment for Railway"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "Error: Not in the Django project directory"
    exit 1
fi

# Show what we're deploying
echo "Changes to deploy:"
echo "1. Enhanced LoginAPIView with guaranteed CORS headers"
echo "2. Universal CORS Middleware for all responses"
echo "3. Error responses with CORS headers"
echo ""

# Git operations
echo "Preparing deployment..."

# Add the new files
git add users/views_api_enhanced.py
git add config/middleware_cors_enhanced.py
git add test_cors_headers.py
git add deploy_cors_fix.sh

# Add modified files
git add users/urls.py
git add config/settings_base.py

# Show status
echo ""
echo "Files to be committed:"
git status --short

echo ""
read -p "Do you want to commit and deploy these changes? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Commit
    git commit -m "fix: Guarantee CORS headers on all responses including errors

- Add EnhancedLoginAPIView with built-in CORS handling
- Implement UniversalCORSMiddleware as first middleware
- Ensure all error responses include CORS headers
- Fix 500 errors returning without CORS headers
- Add comprehensive CORS testing tool

This resolves the CORS policy blocking issue from vlanet.net"

    # Push to Railway
    echo ""
    echo "Pushing to Railway..."
    git push

    echo ""
    echo "=================================="
    echo "Deployment initiated!"
    echo "=================================="
    echo ""
    echo "Next steps:"
    echo "1. Monitor Railway deployment at: https://railway.app/project/..."
    echo "2. Once deployed, run: python3 test_cors_headers.py"
    echo "3. Test from frontend at: https://vlanet.net"
    echo ""
    echo "To verify deployment:"
    echo "  curl -I -X OPTIONS https://videoplanet.up.railway.app/api/users/login/ \\"
    echo "    -H 'Origin: https://vlanet.net' \\"
    echo "    -H 'Access-Control-Request-Method: POST'"
else
    echo "Deployment cancelled."
fi