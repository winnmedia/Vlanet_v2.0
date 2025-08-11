#!/bin/bash

# 배포 검증 자동화 스크립트
# 작성자: Emily (CI/CD Engineer)
# 생성일: 2025-08-11
# 목적: GitHub Actions 배포 후 종합 검증

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 설정 변수
BACKEND_URL="${BACKEND_URL:-https://your-railway-backend.railway.app}"
FRONTEND_URL="${FRONTEND_URL:-https://your-vercel-domain.vercel.app}"
TIMEOUT=30
MAX_RETRIES=5

# 로깅 함수
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "${PURPLE}🔍 $1${NC}"; }

# 시작 배너
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    배포 검증 자동화                          ║"
    echo "║               VideoPlanet Deployment Validator              ║"
    echo "║                                                              ║"
    echo "║  Backend: Railway    Frontend: Vercel    CI/CD: GitHub      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# HTTP 상태 코드 확인
check_http_status() {
    local url=$1
    local expected_status=${2:-200}
    local description=$3
    
    log_step "Testing: $description"
    log_info "URL: $url"
    
    for i in $(seq 1 $MAX_RETRIES); do
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" || echo "000")
        
        if [[ "$status_code" == "$expected_status" ]]; then
            log_success "HTTP $status_code - $description"
            return 0
        else
            log_warning "Attempt $i/$MAX_RETRIES: HTTP $status_code (expected $expected_status)"
            if [[ $i -lt $MAX_RETRIES ]]; then
                sleep 10
            fi
        fi
    done
    
    log_error "Failed: $description (HTTP $status_code)"
    return 1
}

# JSON 응답 검증
check_json_response() {
    local url=$1
    local expected_key=$2
    local description=$3
    
    log_step "Testing: $description"
    
    local response=$(curl -s --max-time $TIMEOUT "$url" || echo "")
    
    if [[ -z "$response" ]]; then
        log_error "No response from $url"
        return 1
    fi
    
    if echo "$response" | jq -e ".$expected_key" > /dev/null 2>&1; then
        log_success "JSON response valid - $description"
        return 0
    else
        log_error "Invalid JSON response - $description"
        log_info "Response: $response"
        return 1
    fi
}

# 성능 테스트
check_performance() {
    local url=$1
    local description=$2
    local max_time=${3:-3000}  # 3초
    
    log_step "Performance test: $description"
    
    local response_time=$(curl -s -o /dev/null -w "%{time_total}" --max-time $TIMEOUT "$url" | cut -d. -f1)
    local response_time_ms=$((response_time * 1000))
    
    if [[ $response_time_ms -lt $max_time ]]; then
        log_success "Performance OK: ${response_time_ms}ms (< ${max_time}ms) - $description"
        return 0
    else
        log_warning "Performance slow: ${response_time_ms}ms (> ${max_time}ms) - $description"
        return 1
    fi
}

# SSL 인증서 확인
check_ssl_certificate() {
    local url=$1
    local description=$2
    
    log_step "SSL Certificate: $description"
    
    local domain=$(echo "$url" | sed -e 's|^https://||' -e 's|/.*||')
    
    if echo | openssl s_client -connect "${domain}:443" -servername "$domain" 2>/dev/null | openssl x509 -noout -dates; then
        log_success "SSL certificate valid - $description"
        return 0
    else
        log_error "SSL certificate issue - $description"
        return 1
    fi
}

# 데이터베이스 연결 확인
check_database_connection() {
    log_step "Database connection test"
    
    local db_health_url="${BACKEND_URL}/health/db/"
    check_http_status "$db_health_url" "200" "Database health check"
}

# Redis 연결 확인  
check_redis_connection() {
    log_step "Redis connection test"
    
    local redis_health_url="${BACKEND_URL}/health/redis/"
    check_http_status "$redis_health_url" "200" "Redis health check"
}

# API 엔드포인트 테스트
test_api_endpoints() {
    log_step "API 엔드포인트 테스트"
    
    local endpoints=(
        "/health/:Health check"
        "/api/users/me/:User profile endpoint"
        "/api/projects/:Projects list"
        "/api/auth/status/:Auth status"
        "/admin/:Admin panel"
    )
    
    local passed=0
    local total=${#endpoints[@]}
    
    for endpoint_info in "${endpoints[@]}"; do
        local endpoint=$(echo "$endpoint_info" | cut -d':' -f1)
        local description=$(echo "$endpoint_info" | cut -d':' -f2)
        
        if check_http_status "${BACKEND_URL}${endpoint}" "200" "$description"; then
            ((passed++))
        fi
    done
    
    log_info "API Tests: $passed/$total passed"
    
    if [[ $passed -eq $total ]]; then
        log_success "All API endpoints accessible"
        return 0
    else
        log_warning "Some API endpoints failed"
        return 1
    fi
}

# 프론트엔드 페이지 테스트
test_frontend_pages() {
    log_step "프론트엔드 페이지 테스트"
    
    local pages=(
        "/:Homepage"
        "/login:Login page" 
        "/signup:Signup page"
        "/dashboard:Dashboard (may redirect)"
        "/projects:Projects page (may redirect)"
    )
    
    local passed=0
    local total=${#pages[@]}
    
    for page_info in "${pages[@]}"; do
        local page=$(echo "$page_info" | cut -d':' -f1)
        local description=$(echo "$page_info" | cut -d':' -f2)
        
        # 인증이 필요한 페이지는 리디렉트 허용 (302, 307)
        if [[ "$page" == "/dashboard" ]] || [[ "$page" == "/projects" ]]; then
            if check_http_status "${FRONTEND_URL}${page}" "200" "$description" || 
               check_http_status "${FRONTEND_URL}${page}" "302" "$description" ||
               check_http_status "${FRONTEND_URL}${page}" "307" "$description"; then
                ((passed++))
            fi
        else
            if check_http_status "${FRONTEND_URL}${page}" "200" "$description"; then
                ((passed++))
            fi
        fi
    done
    
    log_info "Frontend Tests: $passed/$total passed"
    
    if [[ $passed -eq $total ]]; then
        log_success "All frontend pages accessible"
        return 0
    else
        log_warning "Some frontend pages failed"
        return 1
    fi
}

# 보안 헤더 확인
check_security_headers() {
    log_step "보안 헤더 확인"
    
    local headers_to_check=(
        "X-Content-Type-Options"
        "X-Frame-Options"  
        "Referrer-Policy"
        "Content-Security-Policy"
    )
    
    local found_headers=0
    
    for header in "${headers_to_check[@]}"; do
        if curl -s -I --max-time $TIMEOUT "${FRONTEND_URL}" | grep -i "$header" > /dev/null; then
            log_success "Security header found: $header"
            ((found_headers++))
        else
            log_warning "Security header missing: $header"
        fi
    done
    
    log_info "Security headers: $found_headers/${#headers_to_check[@]} found"
    
    if [[ $found_headers -ge 2 ]]; then
        return 0
    else
        return 1
    fi
}

# CORS 설정 확인
check_cors_configuration() {
    log_step "CORS 설정 확인"
    
    local cors_response=$(curl -s -I --max-time $TIMEOUT \
        -H "Origin: ${FRONTEND_URL}" \
        -H "Access-Control-Request-Method: GET" \
        "${BACKEND_URL}/api/auth/status/" | grep -i "access-control")
    
    if [[ -n "$cors_response" ]]; then
        log_success "CORS headers configured"
        return 0
    else
        log_warning "CORS headers not found"
        return 1
    fi
}

# GitHub Actions 워크플로우 상태 확인
check_github_actions_status() {
    log_step "GitHub Actions 워크플로우 상태 확인"
    
    # GitHub CLI가 있는 경우에만 실행
    if command -v gh &> /dev/null; then
        local workflow_status=$(gh run list --limit 5 --json status,conclusion 2>/dev/null || echo "[]")
        
        if [[ "$workflow_status" != "[]" ]]; then
            local successful_runs=$(echo "$workflow_status" | jq '[.[] | select(.conclusion == "success")] | length')
            local total_runs=$(echo "$workflow_status" | jq 'length')
            
            log_info "Recent workflow runs: $successful_runs/$total_runs successful"
            
            if [[ $successful_runs -eq $total_runs ]] && [[ $total_runs -gt 0 ]]; then
                log_success "All recent workflows successful"
                return 0
            else
                log_warning "Some workflows failed or are pending"
                return 1
            fi
        else
            log_info "GitHub CLI not authenticated or no workflow data"
            return 0
        fi
    else
        log_info "GitHub CLI not installed, skipping workflow check"
        return 0
    fi
}

# 종합 리포트 생성
generate_report() {
    local total_tests=$1
    local passed_tests=$2
    local failed_tests=$((total_tests - passed_tests))
    local success_rate=$((passed_tests * 100 / total_tests))
    
    echo ""
    log_step "배포 검증 결과 요약"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}📊 Test Results Summary${NC}"
    echo "  총 테스트: $total_tests"
    echo "  성공: $passed_tests"
    echo "  실패: $failed_tests"
    echo "  성공률: $success_rate%"
    echo ""
    
    if [[ $success_rate -ge 90 ]]; then
        echo -e "${GREEN}🎉 배포 상태: EXCELLENT ($success_rate%)${NC}"
        echo "  모든 주요 기능이 정상적으로 작동합니다."
    elif [[ $success_rate -ge 80 ]]; then
        echo -e "${YELLOW}✅ 배포 상태: GOOD ($success_rate%)${NC}"
        echo "  대부분의 기능이 정상적으로 작동합니다."
    elif [[ $success_rate -ge 70 ]]; then
        echo -e "${YELLOW}⚠️  배포 상태: WARNING ($success_rate%)${NC}"
        echo "  일부 기능에 문제가 있을 수 있습니다."
    else
        echo -e "${RED}🚨 배포 상태: CRITICAL ($success_rate%)${NC}"
        echo "  즉시 문제를 해결해야 합니다."
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    echo -e "${BLUE}🔗 모니터링 링크:${NC}"
    echo "  Backend: $BACKEND_URL"
    echo "  Frontend: $FRONTEND_URL"
    echo "  Railway Dashboard: https://railway.app/dashboard"
    echo "  Vercel Dashboard: https://vercel.com/dashboard"
    echo ""
    
    if [[ $success_rate -lt 80 ]]; then
        echo -e "${RED}🚨 긴급 대응이 필요한 경우:${NC}"
        echo "  1. ./scripts/emergency-rollback.sh 실행"
        echo "  2. Slack #incidents 채널에 알림"
        echo "  3. 온콜 엔지니어에게 연락"
        echo ""
    fi
    
    return $((success_rate >= 80 ? 0 : 1))
}

# 메인 실행 함수
main() {
    print_banner
    
    log_info "배포 검증을 시작합니다..."
    log_info "Backend URL: $BACKEND_URL"
    log_info "Frontend URL: $FRONTEND_URL"
    log_info "Timeout: ${TIMEOUT}s"
    echo ""
    
    # 테스트 실행
    local total_tests=0
    local passed_tests=0
    
    # 1. 기본 연결성 테스트
    echo -e "${PURPLE}🌐 기본 연결성 테스트${NC}"
    ((total_tests++)); check_http_status "$BACKEND_URL/health/" "200" "Backend health check" && ((passed_tests++))
    ((total_tests++)); check_http_status "$FRONTEND_URL" "200" "Frontend homepage" && ((passed_tests++))
    
    # 2. SSL 인증서 테스트
    echo -e "${PURPLE}🔒 SSL 인증서 테스트${NC}"
    ((total_tests++)); check_ssl_certificate "$BACKEND_URL" "Backend SSL" && ((passed_tests++))
    ((total_tests++)); check_ssl_certificate "$FRONTEND_URL" "Frontend SSL" && ((passed_tests++))
    
    # 3. 데이터베이스 연결 테스트
    echo -e "${PURPLE}🗄️  데이터베이스 테스트${NC}"
    ((total_tests++)); check_database_connection && ((passed_tests++))
    ((total_tests++)); check_redis_connection && ((passed_tests++))
    
    # 4. API 엔드포인트 테스트
    echo -e "${PURPLE}🔌 API 엔드포인트 테스트${NC}"
    ((total_tests++)); test_api_endpoints && ((passed_tests++))
    
    # 5. 프론트엔드 페이지 테스트
    echo -e "${PURPLE}💻 프론트엔드 페이지 테스트${NC}"
    ((total_tests++)); test_frontend_pages && ((passed_tests++))
    
    # 6. 성능 테스트
    echo -e "${PURPLE}⚡ 성능 테스트${NC}"
    ((total_tests++)); check_performance "$BACKEND_URL/health/" "Backend response time" 2000 && ((passed_tests++))
    ((total_tests++)); check_performance "$FRONTEND_URL" "Frontend response time" 3000 && ((passed_tests++))
    
    # 7. 보안 테스트
    echo -e "${PURPLE}🛡️  보안 테스트${NC}"
    ((total_tests++)); check_security_headers && ((passed_tests++))
    ((total_tests++)); check_cors_configuration && ((passed_tests++))
    
    # 8. CI/CD 상태 확인
    echo -e "${PURPLE}🔄 CI/CD 상태 확인${NC}"
    ((total_tests++)); check_github_actions_status && ((passed_tests++))
    
    # 최종 리포트 생성
    generate_report $total_tests $passed_tests
}

# 스크립트 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi