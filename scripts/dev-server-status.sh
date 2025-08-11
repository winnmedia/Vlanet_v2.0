#!/bin/bash

# VideoPlanet Development Server Status Monitor
# Author: Robert (DevOps/Platform Lead)
# Created: 2025-08-11
# Purpose: Monitor and display status of all development services

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
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Function to print colored messages
print_header() {
    echo -e "${MAGENTA}$1${NC}"
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

# Function to check service health
check_service_health() {
    local service_name=$1
    local port=$2
    local health_endpoint=$3
    
    if lsof -i :$port >/dev/null 2>&1; then
        local pid=$(lsof -ti :$port 2>/dev/null)
        local memory=$(ps -o rss= -p $pid 2>/dev/null | awk '{printf "%.1f MB", $1/1024}')
        local cpu=$(ps -o %cpu= -p $pid 2>/dev/null | awk '{printf "%.1f%%", $1}')
        
        echo -ne "${GREEN}● RUNNING${NC}"
        echo -ne " │ PID: ${CYAN}$pid${NC}"
        echo -ne " │ CPU: ${CYAN}$cpu${NC}"
        echo -ne " │ MEM: ${CYAN}$memory${NC}"
        
        # Check HTTP health if endpoint provided
        if [ ! -z "$health_endpoint" ]; then
            if curl -s -o /dev/null -w "%{http_code}" "$health_endpoint" | grep -q "200\|301\|302"; then
                echo -e " │ ${GREEN}HTTP OK${NC}"
            else
                echo -e " │ ${YELLOW}HTTP FAIL${NC}"
            fi
        else
            echo ""
        fi
        
        return 0
    else
        echo -e "${RED}● STOPPED${NC}"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    print_header "📊 Database Services"
    echo "────────────────────────────────────────"
    
    # PostgreSQL
    echo -n "PostgreSQL       : "
    if command -v pg_isready &> /dev/null; then
        if pg_isready >/dev/null 2>&1; then
            local pg_version=$(psql --version 2>/dev/null | awk '{print $3}')
            echo -e "${GREEN}● CONNECTED${NC} │ Version: ${CYAN}$pg_version${NC}"
        else
            echo -e "${YELLOW}● LOCAL NOT RUNNING${NC} │ Using Railway database"
        fi
    else
        echo -e "${YELLOW}● NOT INSTALLED${NC} │ Using Railway database"
    fi
    
    # Redis
    echo -n "Redis            : "
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping >/dev/null 2>&1; then
            local redis_version=$(redis-cli --version 2>/dev/null | awk '{print $2}' | cut -d'=' -f2)
            local redis_memory=$(redis-cli info memory 2>/dev/null | grep used_memory_human | cut -d':' -f2 | tr -d '\r')
            echo -e "${GREEN}● CONNECTED${NC} │ Version: ${CYAN}$redis_version${NC} │ Memory: ${CYAN}$redis_memory${NC}"
        else
            echo -e "${RED}● NOT RUNNING${NC}"
        fi
    else
        echo -e "${YELLOW}● NOT INSTALLED${NC}"
    fi
    
    echo ""
}

# Function to check application servers
check_application_servers() {
    print_header "🚀 Application Servers"
    echo "────────────────────────────────────────"
    
    # Django Backend
    echo -n "Django Backend   : "
    check_service_health "Django" $BACKEND_PORT "http://localhost:$BACKEND_PORT/api/health/"
    
    # Next.js Frontend
    echo -n "Next.js Frontend : "
    check_service_health "Next.js" $FRONTEND_PORT "http://localhost:$FRONTEND_PORT"
    
    echo ""
}

# Function to check system resources
check_system_resources() {
    print_header "💻 System Resources"
    echo "────────────────────────────────────────"
    
    # CPU Usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo -n "CPU Usage        : "
    if (( $(echo "$cpu_usage < 70" | bc -l) )); then
        echo -e "${GREEN}$cpu_usage%${NC}"
    elif (( $(echo "$cpu_usage < 90" | bc -l) )); then
        echo -e "${YELLOW}$cpu_usage%${NC}"
    else
        echo -e "${RED}$cpu_usage%${NC}"
    fi
    
    # Memory Usage
    local mem_total=$(free -m | awk 'NR==2{print $2}')
    local mem_used=$(free -m | awk 'NR==2{print $3}')
    local mem_percent=$((mem_used * 100 / mem_total))
    echo -n "Memory Usage     : "
    if [ $mem_percent -lt 70 ]; then
        echo -e "${GREEN}${mem_used}MB / ${mem_total}MB ($mem_percent%)${NC}"
    elif [ $mem_percent -lt 90 ]; then
        echo -e "${YELLOW}${mem_used}MB / ${mem_total}MB ($mem_percent%)${NC}"
    else
        echo -e "${RED}${mem_used}MB / ${mem_total}MB ($mem_percent%)${NC}"
    fi
    
    # Disk Usage
    local disk_usage=$(df -h "$PROJECT_ROOT" | awk 'NR==2{print $5}' | sed 's/%//')
    local disk_info=$(df -h "$PROJECT_ROOT" | awk 'NR==2{print $3 " / " $2}')
    echo -n "Disk Usage       : "
    if [ $disk_usage -lt 70 ]; then
        echo -e "${GREEN}$disk_info ($disk_usage%)${NC}"
    elif [ $disk_usage -lt 90 ]; then
        echo -e "${YELLOW}$disk_info ($disk_usage%)${NC}"
    else
        echo -e "${RED}$disk_info ($disk_usage%)${NC}"
    fi
    
    echo ""
}

# Function to check recent logs
check_recent_logs() {
    print_header "📝 Recent Log Activity"
    echo "────────────────────────────────────────"
    
    if [ -d "$LOG_DIR" ]; then
        # Django logs
        if [ -f "$LOG_DIR/django_server.log" ]; then
            echo "Django Server (last 3 lines):"
            tail -3 "$LOG_DIR/django_server.log" 2>/dev/null | sed 's/^/  /'
        fi
        
        # Next.js logs
        if [ -f "$LOG_DIR/nextjs_server.log" ]; then
            echo "Next.js Server (last 3 lines):"
            tail -3 "$LOG_DIR/nextjs_server.log" 2>/dev/null | sed 's/^/  /'
        fi
    else
        print_warning "Log directory not found"
    fi
    
    echo ""
}

# Function to check API endpoints
check_api_endpoints() {
    print_header "🔌 API Endpoint Health"
    echo "────────────────────────────────────────"
    
    local endpoints=(
        "http://localhost:$BACKEND_PORT/api/health/|Health Check"
        "http://localhost:$BACKEND_PORT/api/users/|Users API"
        "http://localhost:$BACKEND_PORT/api/projects/|Projects API"
        "http://localhost:$BACKEND_PORT/admin/|Admin Panel"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS='|' read -r endpoint name <<< "$endpoint_info"
        echo -n "$name: "
        
        if lsof -i :$BACKEND_PORT >/dev/null 2>&1; then
            local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null)
            case $status_code in
                200|201|204)
                    echo -e "${GREEN}✓ OK ($status_code)${NC}"
                    ;;
                301|302|304)
                    echo -e "${CYAN}↻ Redirect ($status_code)${NC}"
                    ;;
                401|403)
                    echo -e "${YELLOW}🔒 Auth Required ($status_code)${NC}"
                    ;;
                404)
                    echo -e "${YELLOW}⚠ Not Found ($status_code)${NC}"
                    ;;
                500|502|503)
                    echo -e "${RED}✗ Server Error ($status_code)${NC}"
                    ;;
                *)
                    echo -e "${YELLOW}? Unknown ($status_code)${NC}"
                    ;;
            esac
        else
            echo -e "${RED}Server not running${NC}"
        fi
    done
    
    echo ""
}

# Function for continuous monitoring
continuous_monitor() {
    while true; do
        clear
        show_full_status
        echo "────────────────────────────────────────"
        echo "Press Ctrl+C to exit continuous monitoring"
        echo "Refreshing every 5 seconds..."
        sleep 5
    done
}

# Function to show full status
show_full_status() {
    echo "╔════════════════════════════════════════╗"
    echo "║   VideoPlanet Development Environment   ║"
    echo "║         Status Monitor v1.0             ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    
    check_application_servers
    check_database
    check_api_endpoints
    check_system_resources
    
    if [ "${1:-}" != "brief" ]; then
        check_recent_logs
    fi
    
    # URLs
    print_header "🌐 Quick Access URLs"
    echo "────────────────────────────────────────"
    if lsof -i :$FRONTEND_PORT >/dev/null 2>&1; then
        print_success "Frontend:  http://localhost:$FRONTEND_PORT"
    else
        print_error "Frontend:  Not available"
    fi
    
    if lsof -i :$BACKEND_PORT >/dev/null 2>&1; then
        print_success "Backend:   http://localhost:$BACKEND_PORT"
        print_status "API Docs:  http://localhost:$BACKEND_PORT/api/docs"
        print_status "Admin:     http://localhost:$BACKEND_PORT/admin"
    else
        print_error "Backend:   Not available"
    fi
}

# Main execution
main() {
    case "${1:-status}" in
        status)
            show_full_status
            ;;
        brief)
            show_full_status "brief"
            ;;
        monitor)
            continuous_monitor
            ;;
        json)
            # JSON output for programmatic use
            echo "{"
            echo "  \"backend\": $(lsof -i :$BACKEND_PORT >/dev/null 2>&1 && echo "true" || echo "false"),"
            echo "  \"frontend\": $(lsof -i :$FRONTEND_PORT >/dev/null 2>&1 && echo "true" || echo "false"),"
            echo "  \"postgresql\": $(pg_isready >/dev/null 2>&1 && echo "true" || echo "false"),"
            echo "  \"redis\": $(redis-cli ping >/dev/null 2>&1 && echo "true" || echo "false")"
            echo "}"
            ;;
        *)
            echo "Usage: $0 [status|brief|monitor|json]"
            echo "  status  - Show full status (default)"
            echo "  brief   - Show brief status without logs"
            echo "  monitor - Continuous monitoring mode"
            echo "  json    - Output status as JSON"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"