#!/bin/bash

# Process Management Script for Codespaces
# Usage: ./manage.sh [start|stop|status|restart]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

start_services() {
    print_status "Starting AI Email Responder services..."
    
    # Start MongoDB
    print_status "Starting MongoDB..."
    if sudo systemctl start mongod 2>/dev/null; then
        print_success "MongoDB started using systemd"
    elif sudo service mongod start 2>/dev/null; then
        print_success "MongoDB started using service command"
    elif sudo service mongodb start 2>/dev/null; then
        print_success "MongoDB started using mongodb service"
    else
        print_status "Starting MongoDB directly..."
        sudo mkdir -p /data/db
        sudo chown -R $(whoami) /data/db
        mongod --dbpath /data/db --fork --logpath /tmp/mongod.log --bind_ip_all 2>/dev/null || true
    fi
    sleep 3
    
    # Start Backend
    print_status "Starting Backend..."
    cd /app
    source /root/.venv/bin/activate
    nohup uvicorn backend.server:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
    sleep 3
    
    # Start Frontend
    print_status "Starting Frontend..."
    cd /app/frontend
    nohup yarn start > /tmp/frontend.log 2>&1 &
    sleep 5
    
    print_success "All services started!"
}

stop_services() {
    print_status "Stopping AI Email Responder services..."
    
    # Stop Backend
    print_status "Stopping Backend..."
    pkill -f "uvicorn.*backend.server" 2>/dev/null || true
    
    # Stop Frontend
    print_status "Stopping Frontend..."
    pkill -f "yarn.*start" 2>/dev/null || true
    pkill -f "react-scripts.*start" 2>/dev/null || true
    
    # Stop MongoDB (optional)
    # print_status "Stopping MongoDB..."
    # sudo service mongod stop 2>/dev/null || sudo service mongodb stop 2>/dev/null
    
    print_success "Services stopped!"
}

show_status() {
    echo -e "${BLUE}AI Email Responder - Service Status${NC}"
    echo "=================================="
    
    # Check Backend
    if ps aux | grep -v grep | grep 'uvicorn.*backend.server' >/dev/null; then
        echo -e "Backend:  ${GREEN}RUNNING${NC} (Port 8001)"
    else
        echo -e "Backend:  ${RED}STOPPED${NC}"
    fi
    
    # Check Frontend
    if ps aux | grep -v grep | grep 'yarn.*start' >/dev/null; then
        echo -e "Frontend: ${GREEN}RUNNING${NC} (Port 3000)"
    else
        echo -e "Frontend: ${RED}STOPPED${NC}"
    fi
    
    # Check MongoDB
    mongo_status="${RED}STOPPED${NC}"
    if sudo systemctl is-active mongod >/dev/null 2>&1; then
        mongo_status="${GREEN}RUNNING${NC} (systemd)"
    elif service mongod status 2>/dev/null | grep -q 'running\|active'; then
        mongo_status="${GREEN}RUNNING${NC} (service)"
    elif service mongodb status 2>/dev/null | grep -q 'running\|active'; then
        mongo_status="${GREEN}RUNNING${NC} (mongodb service)"
    elif ps aux | grep -v grep | grep 'mongod' >/dev/null; then
        mongo_status="${GREEN}RUNNING${NC} (process)"
    fi
    
    echo -e "MongoDB:  $mongo_status"
    
    echo ""
    echo -e "${BLUE}Application URLs:${NC}"
    echo -e "Frontend: ${YELLOW}http://localhost:3000${NC}"
    echo -e "Backend:  ${YELLOW}http://localhost:8001${NC}"
}

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        show_status
        ;;
    restart)
        stop_services
        sleep 3
        start_services
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all services"
        echo "  stop    - Stop all services"
        echo "  status  - Show service status"
        echo "  restart - Restart all services"
        exit 1
        ;;
esac