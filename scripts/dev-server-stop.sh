#!/bin/bash

# VideoPlanet Development Server Stop Script
# Author: Robert (DevOps/Platform Lead)
# Created: 2025-08-11
# Purpose: Gracefully stop all development services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="/home/winnmedia/VideoPlanet"
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_PORT=8000
FRONTEND_PORT=3000

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

# Function to stop process by PID file
stop_by_pidfile() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            print_status "Stopping $service_name (PID: $pid)..."
            kill -TERM $pid 2>/dev/null || true
            sleep 2
            
            if kill -0 $pid 2>/dev/null; then
                print_warning "Process still running, forcing shutdown..."
                kill -9 $pid 2>/dev/null || true
            fi
            
            rm -f "$pid_file"
            print_success "$service_name stopped"
        else
            print_warning "$service_name PID file exists but process not running"
            rm -f "$pid_file"
        fi
    else
        print_status "$service_name PID file not found"
    fi
}

# Function to stop process by port
stop_by_port() {
    local service_name=$1
    local port=$2
    
    local pid=$(lsof -ti :$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        print_status "Stopping $service_name on port $port (PID: $pid)..."
        kill -TERM $pid 2>/dev/null || true
        sleep 2
        
        if lsof -ti :$port >/dev/null 2>&1; then
            print_warning "Process still running, forcing shutdown..."
            kill -9 $(lsof -ti :$port) 2>/dev/null || true
        fi
        
        print_success "$service_name stopped"
    else
        print_status "$service_name not running on port $port"
    fi
}

# Function to stop all Node.js dev servers
stop_nodejs_servers() {
    print_status "Stopping all Node.js development servers..."
    
    # Find and kill all npm run dev processes
    pkill -f "npm run dev" 2>/dev/null || true
    
    # Find and kill all next dev processes
    pkill -f "next dev" 2>/dev/null || true
    
    # Clean up any orphaned node processes on our ports
    for port in 3000 3001 3002; do
        local pid=$(lsof -ti :$port 2>/dev/null)
        if [ ! -z "$pid" ]; then
            print_warning "Cleaning up orphaned process on port $port"
            kill -9 $pid 2>/dev/null || true
        fi
    done
}

# Function to stop all Python dev servers
stop_python_servers() {
    print_status "Stopping all Python development servers..."
    
    # Find and kill all Django runserver processes
    pkill -f "manage.py runserver" 2>/dev/null || true
    
    # Clean up any orphaned python processes on our ports
    for port in 8000 8001 8002; do
        local pid=$(lsof -ti :$port 2>/dev/null)
        if [ ! -z "$pid" ]; then
            local process_name=$(ps -p $pid -o comm= 2>/dev/null)
            if [[ "$process_name" == *"python"* ]]; then
                print_warning "Cleaning up orphaned Python process on port $port"
                kill -9 $pid 2>/dev/null || true
            fi
        fi
    done
}

# Main execution
main() {
    echo "====================================="
    echo "   VideoPlanet Development Server"
    echo "        Stop Script v1.0"
    echo "====================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-all}" in
        backend)
            print_status "Stopping backend services..."
            stop_by_pidfile "Django server" "$LOG_DIR/django.pid"
            stop_by_port "Django server" $BACKEND_PORT
            stop_python_servers
            ;;
        frontend)
            print_status "Stopping frontend services..."
            stop_by_pidfile "Next.js server" "$LOG_DIR/nextjs.pid"
            stop_by_port "Next.js server" $FRONTEND_PORT
            stop_nodejs_servers
            ;;
        all)
            print_status "Stopping all services..."
            
            # Stop using PID files first
            stop_by_pidfile "Django server" "$LOG_DIR/django.pid"
            stop_by_pidfile "Next.js server" "$LOG_DIR/nextjs.pid"
            
            # Then stop by port
            stop_by_port "Django server" $BACKEND_PORT
            stop_by_port "Next.js server" $FRONTEND_PORT
            
            # Finally, clean up any remaining processes
            stop_python_servers
            stop_nodejs_servers
            ;;
        clean)
            print_status "Performing clean shutdown..."
            
            # Stop all services
            stop_by_pidfile "Django server" "$LOG_DIR/django.pid"
            stop_by_pidfile "Next.js server" "$LOG_DIR/nextjs.pid"
            stop_by_port "Django server" $BACKEND_PORT
            stop_by_port "Next.js server" $FRONTEND_PORT
            stop_python_servers
            stop_nodejs_servers
            
            # Clean up log files
            print_status "Cleaning up log files..."
            rm -f "$LOG_DIR"/*.log
            rm -f "$LOG_DIR"/*.pid
            print_success "Clean shutdown complete"
            ;;
        *)
            echo "Usage: $0 [all|backend|frontend|clean]"
            echo "  all      - Stop all services (default)"
            echo "  backend  - Stop only backend services"
            echo "  frontend - Stop only frontend services"
            echo "  clean    - Stop all services and clean logs"
            exit 1
            ;;
    esac
    
    echo ""
    echo "====================================="
    print_success "Shutdown complete!"
    echo "====================================="
}

# Run main function
main "$@"