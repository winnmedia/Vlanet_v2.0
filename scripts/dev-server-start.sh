#!/bin/bash

# VideoPlanet Development Server Startup Script
# Author: Robert (DevOps/Platform Lead)
# Created: 2025-08-11
# Purpose: Automated startup of local development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/winnmedia/VideoPlanet"
BACKEND_DIR="$PROJECT_ROOT/vridge_back"
FRONTEND_DIR="$PROJECT_ROOT/vridge_front"
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        print_warning "Killing existing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Function to start PostgreSQL (if available)
start_postgresql() {
    print_status "Checking PostgreSQL status..."
    
    if command -v pg_isready &> /dev/null; then
        if pg_isready >/dev/null 2>&1; then
            print_success "PostgreSQL is already running"
        else
            print_warning "PostgreSQL is not running. Attempting to start..."
            if command -v systemctl &> /dev/null; then
                sudo systemctl start postgresql 2>/dev/null || true
            elif command -v service &> /dev/null; then
                sudo service postgresql start 2>/dev/null || true
            fi
            
            sleep 3
            if pg_isready >/dev/null 2>&1; then
                print_success "PostgreSQL started successfully"
            else
                print_warning "Could not start PostgreSQL. Using Railway database instead."
            fi
        fi
    else
        print_warning "PostgreSQL client not found. Using Railway database."
    fi
}

# Function to start Redis (if available)
start_redis() {
    print_status "Checking Redis status..."
    
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping >/dev/null 2>&1; then
            print_success "Redis is already running"
        else
            print_warning "Redis is not running. Attempting to start..."
            if command -v systemctl &> /dev/null; then
                sudo systemctl start redis 2>/dev/null || true
            elif command -v service &> /dev/null; then
                sudo service redis-server start 2>/dev/null || true
            elif command -v redis-server &> /dev/null; then
                redis-server --daemonize yes 2>/dev/null || true
            fi
            
            sleep 2
            if redis-cli ping >/dev/null 2>&1; then
                print_success "Redis started successfully"
            else
                print_warning "Could not start Redis. Some caching features may be unavailable."
            fi
        fi
    else
        print_warning "Redis not found. Caching features will be limited."
    fi
}

# Function to start Django backend
start_backend() {
    print_status "Starting Django backend server..."
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        print_status "Activating virtual environment..."
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        print_status "Activating virtual environment..."
        source .venv/bin/activate
    fi
    
    # Check for pending migrations
    print_status "Checking for pending migrations..."
    python3 manage.py showmigrations --plan | tail -5
    
    # Apply migrations if needed
    print_status "Applying database migrations..."
    python3 manage.py migrate --noinput 2>&1 | tee "$LOG_DIR/django_migrate.log"
    
    # Collect static files
    print_status "Collecting static files..."
    python3 manage.py collectstatic --noinput 2>&1 | tee "$LOG_DIR/django_collectstatic.log"
    
    # Kill existing process on port if exists
    if check_port $BACKEND_PORT; then
        print_warning "Port $BACKEND_PORT is already in use"
        kill_port $BACKEND_PORT
    fi
    
    # Start Django server
    print_status "Starting Django development server on port $BACKEND_PORT..."
    nohup python3 manage.py runserver 0.0.0.0:$BACKEND_PORT > "$LOG_DIR/django_server.log" 2>&1 &
    local django_pid=$!
    
    sleep 3
    
    if kill -0 $django_pid 2>/dev/null; then
        print_success "Django server started successfully (PID: $django_pid)"
        echo $django_pid > "$LOG_DIR/django.pid"
    else
        print_error "Failed to start Django server. Check logs at $LOG_DIR/django_server.log"
        return 1
    fi
}

# Function to start Next.js frontend
start_frontend() {
    print_status "Starting Next.js frontend server..."
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Installing dependencies..."
        npm install 2>&1 | tee "$LOG_DIR/npm_install.log"
    fi
    
    # Kill existing process on port if exists
    if check_port $FRONTEND_PORT; then
        print_warning "Port $FRONTEND_PORT is already in use"
        kill_port $FRONTEND_PORT
    fi
    
    # Start Next.js server
    print_status "Starting Next.js development server on port $FRONTEND_PORT..."
    PORT=$FRONTEND_PORT nohup npm run dev > "$LOG_DIR/nextjs_server.log" 2>&1 &
    local nextjs_pid=$!
    
    sleep 5
    
    if kill -0 $nextjs_pid 2>/dev/null; then
        print_success "Next.js server started successfully (PID: $nextjs_pid)"
        echo $nextjs_pid > "$LOG_DIR/nextjs.pid"
    else
        print_error "Failed to start Next.js server. Check logs at $LOG_DIR/nextjs_server.log"
        return 1
    fi
}

# Function to show server status
show_status() {
    echo ""
    echo "====================================="
    echo "   Development Server Status"
    echo "====================================="
    
    if check_port $BACKEND_PORT; then
        print_success "Django Backend:  http://localhost:$BACKEND_PORT ✓"
        print_status "  API Docs:      http://localhost:$BACKEND_PORT/api/docs"
        print_status "  Admin Panel:   http://localhost:$BACKEND_PORT/admin"
    else
        print_error "Django Backend: Not running ✗"
    fi
    
    if check_port $FRONTEND_PORT; then
        print_success "Next.js Frontend: http://localhost:$FRONTEND_PORT ✓"
    else
        print_error "Next.js Frontend: Not running ✗"
    fi
    
    echo ""
    print_status "Logs directory: $LOG_DIR"
    print_status "Use 'tail -f $LOG_DIR/<service>.log' to view logs"
    echo "====================================="
}

# Main execution
main() {
    echo "====================================="
    echo "   VideoPlanet Development Server"
    echo "        Startup Script v1.0"
    echo "====================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-all}" in
        backend)
            start_postgresql
            start_redis
            start_backend
            ;;
        frontend)
            start_frontend
            ;;
        services)
            start_postgresql
            start_redis
            ;;
        all)
            start_postgresql
            start_redis
            start_backend
            start_frontend
            ;;
        *)
            echo "Usage: $0 [all|backend|frontend|services]"
            echo "  all      - Start all services (default)"
            echo "  backend  - Start only backend services"
            echo "  frontend - Start only frontend service"
            echo "  services - Start only PostgreSQL and Redis"
            exit 1
            ;;
    esac
    
    show_status
    
    print_success "Development environment is ready!"
    print_status "Press Ctrl+C to stop monitoring. Servers will continue running in background."
    print_status "Use './scripts/dev-server-stop.sh' to stop all services."
}

# Run main function
main "$@"