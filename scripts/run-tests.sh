#!/bin/bash

# VideoPlanet Test Runner Script
# Author: Robert (DevOps/Platform Lead)
# Created: 2025-08-11
# Purpose: Automated test execution with detailed reporting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="/home/winnmedia/VideoPlanet"
BACKEND_DIR="$PROJECT_ROOT/vridge_back"
FRONTEND_DIR="$PROJECT_ROOT/vridge_front"
TEST_REPORT_DIR="$PROJECT_ROOT/test-reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Test metrics
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Create test report directory
mkdir -p "$TEST_REPORT_DIR"

# Function to print colored messages
print_header() {
    echo -e "\n${MAGENTA}═══════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  $1${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to run Django tests
run_django_tests() {
    print_header "Running Django Backend Tests"
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    local test_output="$TEST_REPORT_DIR/django_test_$TIMESTAMP.log"
    local test_result=0
    
    print_status "Executing Django unit tests..."
    
    # Run tests with coverage
    if python3 manage.py test --verbosity=2 --keepdb 2>&1 | tee "$test_output"; then
        print_success "Django tests completed successfully"
        test_result=0
    else
        print_error "Django tests failed"
        test_result=1
    fi
    
    # Parse test results
    local django_passed=$(grep -oP '\d+(?= passed)' "$test_output" 2>/dev/null | tail -1 || echo "0")
    local django_failed=$(grep -oP '\d+(?= failed)' "$test_output" 2>/dev/null | tail -1 || echo "0")
    local django_errors=$(grep -oP '\d+(?= error)' "$test_output" 2>/dev/null | tail -1 || echo "0")
    
    if [ -z "$django_passed" ]; then django_passed=0; fi
    if [ -z "$django_failed" ]; then django_failed=0; fi
    if [ -z "$django_errors" ]; then django_errors=0; fi
    
    django_failed=$((django_failed + django_errors))
    
    TOTAL_TESTS=$((TOTAL_TESTS + django_passed + django_failed))
    PASSED_TESTS=$((PASSED_TESTS + django_passed))
    FAILED_TESTS=$((FAILED_TESTS + django_failed))
    
    echo ""
    echo "Django Test Results:"
    echo "  Passed: $django_passed"
    echo "  Failed: $django_failed"
    echo "  Report: $test_output"
    
    return $test_result
}

# Function to run Next.js tests
run_nextjs_tests() {
    print_header "Running Next.js Frontend Tests"
    
    cd "$FRONTEND_DIR"
    
    local test_output="$TEST_REPORT_DIR/nextjs_test_$TIMESTAMP.log"
    local test_result=0
    
    print_status "Executing Next.js unit tests..."
    
    # Check if test script exists in package.json
    if grep -q '"test"' package.json; then
        if npm test -- --watchAll=false --coverage 2>&1 | tee "$test_output"; then
            print_success "Next.js tests completed successfully"
            test_result=0
        else
            print_error "Next.js tests failed"
            test_result=1
        fi
        
        # Parse Jest test results
        local nextjs_passed=$(grep -oP '\d+(?= passed)' "$test_output" 2>/dev/null | tail -1 || echo "0")
        local nextjs_failed=$(grep -oP '\d+(?= failed)' "$test_output" 2>/dev/null | tail -1 || echo "0")
        local nextjs_skipped=$(grep -oP '\d+(?= skipped)' "$test_output" 2>/dev/null | tail -1 || echo "0")
        
        if [ -z "$nextjs_passed" ]; then nextjs_passed=0; fi
        if [ -z "$nextjs_failed" ]; then nextjs_failed=0; fi
        if [ -z "$nextjs_skipped" ]; then nextjs_skipped=0; fi
        
        TOTAL_TESTS=$((TOTAL_TESTS + nextjs_passed + nextjs_failed + nextjs_skipped))
        PASSED_TESTS=$((PASSED_TESTS + nextjs_passed))
        FAILED_TESTS=$((FAILED_TESTS + nextjs_failed))
        SKIPPED_TESTS=$((SKIPPED_TESTS + nextjs_skipped))
        
        echo ""
        echo "Next.js Test Results:"
        echo "  Passed: $nextjs_passed"
        echo "  Failed: $nextjs_failed"
        echo "  Skipped: $nextjs_skipped"
        echo "  Report: $test_output"
    else
        print_warning "No test script found in package.json"
        test_result=0
    fi
    
    return $test_result
}

# Function to run linting checks
run_linting() {
    print_header "Running Code Quality Checks"
    
    local lint_output="$TEST_REPORT_DIR/lint_$TIMESTAMP.log"
    local lint_errors=0
    
    # Python linting (Django)
    print_status "Running Python linting..."
    cd "$BACKEND_DIR"
    
    if command -v flake8 &> /dev/null; then
        if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics 2>&1 | tee -a "$lint_output"; then
            print_success "Python linting passed"
        else
            print_warning "Python linting found issues"
            lint_errors=$((lint_errors + 1))
        fi
    else
        print_warning "flake8 not installed, skipping Python linting"
    fi
    
    # JavaScript/TypeScript linting (Next.js)
    print_status "Running JavaScript/TypeScript linting..."
    cd "$FRONTEND_DIR"
    
    if [ -f "package.json" ] && grep -q '"lint"' package.json; then
        if npm run lint 2>&1 | tee -a "$lint_output"; then
            print_success "JavaScript/TypeScript linting passed"
        else
            print_warning "JavaScript/TypeScript linting found issues"
            lint_errors=$((lint_errors + 1))
        fi
    else
        print_warning "No lint script found, skipping JavaScript linting"
    fi
    
    echo ""
    echo "Linting Report: $lint_output"
    
    return $lint_errors
}

# Function to run security checks
run_security_checks() {
    print_header "Running Security Checks"
    
    local security_output="$TEST_REPORT_DIR/security_$TIMESTAMP.log"
    local security_issues=0
    
    # Python security check
    print_status "Checking Python dependencies for vulnerabilities..."
    cd "$BACKEND_DIR"
    
    if command -v safety &> /dev/null; then
        if safety check --json 2>&1 | tee "$security_output"; then
            print_success "No Python security vulnerabilities found"
        else
            print_warning "Python security vulnerabilities detected"
            security_issues=$((security_issues + 1))
        fi
    else
        print_warning "safety not installed, skipping Python security check"
    fi
    
    # Node.js security check
    print_status "Checking Node.js dependencies for vulnerabilities..."
    cd "$FRONTEND_DIR"
    
    if npm audit --json 2>&1 | tee -a "$security_output"; then
        print_success "No Node.js security vulnerabilities found"
    else
        print_warning "Node.js security vulnerabilities detected"
        security_issues=$((security_issues + 1))
    fi
    
    echo ""
    echo "Security Report: $security_output"
    
    return $security_issues
}

# Function to run integration tests
run_integration_tests() {
    print_header "Running Integration Tests"
    
    local integration_output="$TEST_REPORT_DIR/integration_$TIMESTAMP.log"
    
    print_status "Checking if servers are running..."
    
    # Check if backend is running
    if ! lsof -i :8000 >/dev/null 2>&1; then
        print_warning "Backend server not running. Starting it..."
        "$PROJECT_ROOT/scripts/dev-server-start.sh" backend >/dev/null 2>&1 &
        sleep 5
    fi
    
    # Check if frontend is running
    if ! lsof -i :3000 >/dev/null 2>&1; then
        print_warning "Frontend server not running. Starting it..."
        "$PROJECT_ROOT/scripts/dev-server-start.sh" frontend >/dev/null 2>&1 &
        sleep 5
    fi
    
    print_status "Running API integration tests..."
    
    # Test API endpoints
    local endpoints=(
        "http://localhost:8000/api/health/"
        "http://localhost:8000/api/users/"
        "http://localhost:8000/api/projects/"
    )
    
    local api_tests_passed=0
    local api_tests_failed=0
    
    for endpoint in "${endpoints[@]}"; do
        echo -n "Testing $endpoint... " | tee -a "$integration_output"
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null)
        
        if [[ "$status_code" =~ ^(200|201|204|301|302|401|403)$ ]]; then
            echo "PASS (HTTP $status_code)" | tee -a "$integration_output"
            api_tests_passed=$((api_tests_passed + 1))
        else
            echo "FAIL (HTTP $status_code)" | tee -a "$integration_output"
            api_tests_failed=$((api_tests_failed + 1))
        fi
    done
    
    TOTAL_TESTS=$((TOTAL_TESTS + api_tests_passed + api_tests_failed))
    PASSED_TESTS=$((PASSED_TESTS + api_tests_passed))
    FAILED_TESTS=$((FAILED_TESTS + api_tests_failed))
    
    echo ""
    echo "Integration Test Results:"
    echo "  Passed: $api_tests_passed"
    echo "  Failed: $api_tests_failed"
    echo "  Report: $integration_output"
}

# Function to generate test summary
generate_summary() {
    local summary_file="$TEST_REPORT_DIR/summary_$TIMESTAMP.json"
    
    cat > "$summary_file" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "total_tests": $TOTAL_TESTS,
  "passed": $PASSED_TESTS,
  "failed": $FAILED_TESTS,
  "skipped": $SKIPPED_TESTS,
  "pass_rate": $(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc 2>/dev/null || echo "0"),
  "reports": {
    "django": "$TEST_REPORT_DIR/django_test_$TIMESTAMP.log",
    "nextjs": "$TEST_REPORT_DIR/nextjs_test_$TIMESTAMP.log",
    "lint": "$TEST_REPORT_DIR/lint_$TIMESTAMP.log",
    "security": "$TEST_REPORT_DIR/security_$TIMESTAMP.log",
    "integration": "$TEST_REPORT_DIR/integration_$TIMESTAMP.log"
  }
}
EOF
    
    print_header "Test Summary"
    
    echo "╔════════════════════════════════════════╗"
    echo "║          TEST EXECUTION SUMMARY         ║"
    echo "╠════════════════════════════════════════╣"
    printf "║ Total Tests:    %-23d ║\n" $TOTAL_TESTS
    printf "║ ${GREEN}Passed:${NC}         %-23d ║\n" $PASSED_TESTS
    printf "║ ${RED}Failed:${NC}         %-23d ║\n" $FAILED_TESTS
    printf "║ ${YELLOW}Skipped:${NC}        %-23d ║\n" $SKIPPED_TESTS
    
    if [ $TOTAL_TESTS -gt 0 ]; then
        local pass_rate=$(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc)
        printf "║ Pass Rate:      %-22s%% ║\n" $pass_rate
    fi
    
    echo "╠════════════════════════════════════════╣"
    echo "║ Reports saved to:                       ║"
    echo "║ $TEST_REPORT_DIR"
    echo "╚════════════════════════════════════════╝"
    
    echo ""
    echo "Summary JSON: $summary_file"
    
    # Return exit code based on test results
    if [ $FAILED_TESTS -eq 0 ]; then
        print_success "All tests passed successfully!"
        return 0
    else
        print_error "Some tests failed. Please review the reports."
        return 1
    fi
}

# Main execution
main() {
    echo "╔════════════════════════════════════════╗"
    echo "║     VideoPlanet Test Suite Runner      ║"
    echo "║              Version 1.0                ║"
    echo "╚════════════════════════════════════════╝"
    
    local exit_code=0
    
    case "${1:-all}" in
        backend)
            run_django_tests || exit_code=$?
            ;;
        frontend)
            run_nextjs_tests || exit_code=$?
            ;;
        lint)
            run_linting || exit_code=$?
            ;;
        security)
            run_security_checks || exit_code=$?
            ;;
        integration)
            run_integration_tests || exit_code=$?
            ;;
        all)
            run_django_tests || exit_code=$?
            run_nextjs_tests || exit_code=$?
            run_linting || true  # Don't fail on linting
            run_security_checks || true  # Don't fail on security
            run_integration_tests || exit_code=$?
            ;;
        *)
            echo "Usage: $0 [all|backend|frontend|lint|security|integration]"
            echo "  all         - Run all tests (default)"
            echo "  backend     - Run Django backend tests only"
            echo "  frontend    - Run Next.js frontend tests only"
            echo "  lint        - Run linting checks only"
            echo "  security    - Run security checks only"
            echo "  integration - Run integration tests only"
            exit 1
            ;;
    esac
    
    generate_summary
    
    exit $exit_code
}

# Run main function
main "$@"