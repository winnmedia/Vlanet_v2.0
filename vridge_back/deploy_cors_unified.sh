#!/bin/bash

# CORS Unified Deployment Script
# Arthur, Chief Architect - 2025-08-12
# 
# This script ensures safe deployment of the unified CORS solution to Railway

set -e  # Exit on error

echo "=================================================="
echo "CORS UNIFIED DEPLOYMENT SCRIPT"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Run local tests
echo -e "${YELLOW}Step 1: Running local CORS tests...${NC}"
python test_cors_unified.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Local tests passed${NC}"
else
    echo -e "${RED}✗ Local tests failed. Aborting deployment.${NC}"
    exit 1
fi

# Step 2: Check for conflicting middleware
echo -e "\n${YELLOW}Step 2: Checking for middleware conflicts...${NC}"
if grep -q "middleware_cors_enhanced\|EmergencyCORSMiddleware\|GuaranteedCORSMiddleware" config/settings_base.py; then
    echo -e "${RED}✗ Found conflicting middleware in settings_base.py${NC}"
    echo "Please remove old CORS middleware references"
    exit 1
fi

if grep -q "corsheaders.middleware.CorsMiddleware" config/settings_base.py; then
    echo -e "${RED}✗ Found django-cors-headers middleware still active${NC}"
    echo "The unified middleware replaces django-cors-headers"
    exit 1
fi

echo -e "${GREEN}✓ No middleware conflicts found${NC}"

# Step 3: Validate settings
echo -e "\n${YELLOW}Step 3: Validating CORS settings...${NC}"
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
import django
django.setup()
from django.conf import settings

required_settings = [
    'CORS_ALLOWED_ORIGINS',
    'CORS_ALLOW_CREDENTIALS',
    'CORS_ALLOW_METHODS',
    'CORS_ALLOW_HEADERS'
]

missing = []
for setting in required_settings:
    if not hasattr(settings, setting):
        missing.append(setting)

if missing:
    print(f'Missing settings: {missing}')
    exit(1)

# Check vlanet.net is in allowed origins
allowed = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
required_origins = ['https://vlanet.net', 'https://www.vlanet.net']
for origin in required_origins:
    if origin not in allowed:
        print(f'Required origin {origin} not in CORS_ALLOWED_ORIGINS')
        exit(1)

print('✓ All required CORS settings present')
"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ CORS settings validation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ CORS settings validated${NC}"

# Step 4: Create deployment checklist
echo -e "\n${YELLOW}Step 4: Pre-deployment checklist${NC}"
echo ""
echo "Please confirm the following before deployment:"
echo ""
echo "[ ] 1. You have committed all changes"
echo "[ ] 2. You have tested the login flow locally"
echo "[ ] 3. You have backed up the current production settings"
echo "[ ] 4. You are ready to monitor the deployment"
echo ""
read -p "Have you completed all items? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
    echo -e "${RED}Deployment cancelled${NC}"
    exit 1
fi

# Step 5: Git operations
echo -e "\n${YELLOW}Step 5: Preparing git commit...${NC}"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Uncommitted changes detected:"
    git status --short
    echo ""
    read -p "Do you want to commit these changes? (yes/no): " commit_confirm
    
    if [ "$commit_confirm" == "yes" ]; then
        git add config/middleware_cors_unified.py
        git add config/settings_base.py
        git add test_cors_unified.py
        git add deploy_cors_unified.sh
        
        git commit -m "fix: Implement unified CORS middleware architecture

- Replace multiple CORS middleware with single unified solution
- Guarantee CORS headers on all responses including errors
- Simplify middleware stack for better performance
- Add comprehensive test suite for CORS validation

Resolves: CORS policy violations on vlanet.net
Architecture Decision: Single source of truth for CORS handling"
        
        echo -e "${GREEN}✓ Changes committed${NC}"
    else
        echo -e "${RED}Please commit changes manually before deployment${NC}"
        exit 1
    fi
fi

# Step 6: Push to Railway
echo -e "\n${YELLOW}Step 6: Deploying to Railway...${NC}"
echo ""
echo "To deploy to Railway, run:"
echo ""
echo "  git push origin main"
echo ""
echo "Then monitor the deployment at:"
echo "  https://railway.app/project/[your-project-id]"
echo ""
echo "After deployment, test with:"
echo "  curl -X OPTIONS https://videoplanet.up.railway.app/api/users/login/ \\"
echo "    -H 'Origin: https://vlanet.net' \\"
echo "    -H 'Access-Control-Request-Method: POST' \\"
echo "    -H 'Access-Control-Request-Headers: content-type' -v"
echo ""
echo -e "${GREEN}=================================================="
echo "DEPLOYMENT PREPARATION COMPLETE"
echo "=================================================="
echo -e "${NC}"
echo "Next steps:"
echo "1. Push to git: git push origin main"
echo "2. Monitor Railway deployment logs"
echo "3. Test CORS from vlanet.net"
echo "4. Check error tracking for any issues"
echo ""