#!/bin/bash

# VideoPlanet Git Cleanup Script
# Date: 2025-08-11
# Purpose: Clean up 489 uncommitted files systematically

echo "=========================================="
echo "VideoPlanet Git Cleanup Script"
echo "=========================================="
echo ""

# Step 1: Remove test and temporary files that are now in .gitignore
echo "Step 1: Removing test and temporary files..."
echo "-----------------------------------------"

# Backend test files
cd vridge_back
rm -f check_*.py test_*.py create_*.py debug_*.py emergency_*.py diagnose_*.py force_*.py
rm -f simple_*.py minimal_*.py standalone_*.py server_django_proxy*.py server_with_django.py
rm -f railway_debug.py railway_test.py railway_migrate.py
rm -f generate_models_from_api.py enhanced_model_generator.py template_model_generator.py
rm -f fix_remaining_404.py create_all_missing_urls.py create_invitations_tables.py
rm -f test_allowed_hosts.py test_no_errors.py test_simple_validation.py test_system_integration*.py
rm -f final_integration_test.py direct_migrate.py reset_and_migrate.py migration_health.py
rm -f health_server.py health_test.py health_check.py deployment_checklist.py wait_for_db.py
rm -f django_health_monitor.py qa_*.py comprehensive_*.py example_*.py
rm -f deployment_health_check.sh pre_deploy_check.sh deploy_railway.sh
rm -rf backup_settings/ migrations_enhanced/ migrations_from_spec/

# Remove temporary improved/fixed files
find . -name "*_improved.py" -delete
find . -name "*_fixed.py" -delete
find . -name "*_enhanced.py" -delete
find . -name "*_safe.py" -delete
find . -name "*_compatibility.py" -delete
find . -name "workflow_views.py" -delete

# Remove api_urls.py files (temporary)
find . -name "api_urls.py" -delete

# Remove application/domain directories
find . -type d -name "application" -exec rm -rf {} + 2>/dev/null
find . -type d -name "domain" -exec rm -rf {} + 2>/dev/null

# Remove config/static_settings.py
rm -f config/static_settings.py

# Remove report files
rm -f qa_test_report.md final_success_report.md debug_completion_report.md

cd ..

# Frontend test files
cd vridge_front
rm -f test-*.js deployment-test.js integration-test.js final-test.js
rm -f test-login.js test-auth-flow.js
rm -f tests/frontend-validation-test.js tests/user-journey-test.js tests/comprehensive-integration-test.js
rm -f *test-results*.json *test-report*.json routing-test-report*.json
rm -f scripts/validate-vercel-env.js scripts/vercel-deploy.sh scripts/vercel-health-check.js

cd ..

# Root level files
rm -f deployment_health_check.sh remove_emojis.py
rm -rf quality/ tests/performance/ scripts/
rm -f QA_STRATEGY.md

echo ""
echo "Step 2: Checking git status after cleanup..."
echo "-----------------------------------------"
git status --short | wc -l
echo "files remaining uncommitted"

echo ""
echo "Step 3: Files to be committed (categorized):"
echo "-----------------------------------------"

# Show remaining modified files by category
echo ""
echo "Configuration files:"
git status --short | grep -E "\.json$|\.md$|\.yml$|\.yaml$|\.toml$" | head -20

echo ""
echo "Source code files:"
git status --short | grep -E "\.py$|\.js$|\.jsx$|\.ts$|\.tsx$" | head -20

echo ""
echo "GitHub Actions:"
git status --short | grep ".github/"

echo ""
echo "Documentation:"
git status --short | grep -E "\.md$" | grep -v "MEMORY.md"

echo ""
echo "=========================================="
echo "Cleanup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review remaining files with: git status"
echo "2. Add .gitignore files first: git add */.gitignore .gitignore"
echo "3. Commit core source changes: git add -u (updates to tracked files)"
echo "4. Commit new important files selectively"
echo "5. Final check: git status"