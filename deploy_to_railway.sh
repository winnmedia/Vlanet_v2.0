#!/bin/bash
# Railway Deployment Script
# Chief Architect's deployment orchestrator

echo "🚀 Railway Deployment Preparation"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Step 1: Clean up old Railway files
echo ""
echo "📦 Step 1: Cleaning up legacy Railway files..."
cd vridge_back

# List of files to clean up
OLD_FILES=(
    "railway_*.py"
    "test_railway_*.py"
    "check_railway_*.py"
    "deploy_railway*.sh"
    "fix_railway*.py"
    "Procfile.*"
    ".railway-*"
    "railway_*.sh"
    "create_railway_*.py"
    "diagnose_railway*.py"
    "emergency_railway*.py"
    "force_migrate_railway.py"
)

for pattern in "${OLD_FILES[@]}"; do
    count=$(ls -1 $pattern 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        print_warning "Moving $count files matching $pattern to .backup/"
        mkdir -p .backup/old_railway_files
        mv $pattern .backup/old_railway_files/ 2>/dev/null
    fi
done

cd ..

# Step 2: Verify critical files
echo ""
echo "📋 Step 2: Verifying deployment files..."

REQUIRED_FILES=(
    "railway_wsgi.py"
    "railway_migration.py"
    "railway_collectstatic.py"
    "Procfile"
    "nixpacks.toml"
    "railway.json"
    "vridge_back/requirements.txt"
    "vridge_back/config/settings/railway.py"
)

all_good=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status "$file exists"
    else
        print_error "$file is missing!"
        all_good=false
    fi
done

if [ "$all_good" = false ]; then
    print_error "Some required files are missing. Deployment cannot proceed."
    exit 1
fi

# Step 3: Test Railway WSGI
echo ""
echo "🧪 Step 3: Testing Railway WSGI wrapper..."

python3 -c "import railway_wsgi; print('✅ WSGI wrapper loads successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    print_status "WSGI wrapper test passed"
else
    print_error "WSGI wrapper test failed"
    exit 1
fi

# Step 4: Check environment variables
echo ""
echo "🔐 Step 4: Checking environment variables..."

if [ -z "$RAILWAY_TOKEN" ]; then
    print_warning "RAILWAY_TOKEN not set. You'll need to login manually."
fi

# Step 5: Display deployment checklist
echo ""
echo "📝 Step 5: Pre-deployment Checklist"
echo "-----------------------------------"
echo ""
echo "Please ensure the following environment variables are set in Railway:"
echo ""
echo "  ✓ DATABASE_URL (PostgreSQL connection string)"
echo "  ✓ SECRET_KEY (Django secret key)"
echo "  ✓ DJANGO_SECRET_KEY (backup secret key)"
echo "  ✓ DEBUG=False (for production)"
echo "  ✓ RAILWAY_ENVIRONMENT (set automatically by Railway)"
echo ""
echo "Optional but recommended:"
echo "  ○ REDIS_URL (for caching)"
echo "  ○ EMAIL_HOST_PASSWORD (for email functionality)"
echo "  ○ ALLOWED_HOSTS (additional domains)"
echo ""

# Step 6: Git status check
echo "📊 Step 6: Git Status"
echo "-------------------"
git status --short

echo ""
echo "🎯 Deployment Commands"
echo "====================="
echo ""
echo "1. Commit your changes:"
echo "   ${GREEN}git add -A && git commit -m 'fix: Railway deployment architecture'${NC}"
echo ""
echo "2. Push to Railway:"
echo "   ${GREEN}git push${NC}"
echo ""
echo "3. Or use Railway CLI:"
echo "   ${GREEN}railway up${NC}"
echo ""
echo "4. Monitor deployment:"
echo "   ${GREEN}railway logs${NC}"
echo ""
echo "5. Check health endpoint:"
echo "   ${GREEN}curl https://videoplanet.up.railway.app/health/${NC}"
echo ""

print_status "Deployment preparation complete!"