#!/bin/bash

# AI Email Responder - Complete Setup Script
# This script sets up the entire application with one command
# Usage: ./setup.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_header() {
    echo -e "${BLUE}
╔══════════════════════════════════════════════════════════════╗
║                  AI Email Responder Setup                   ║
║                Complete Application Setup                    ║
╚══════════════════════════════════════════════════════════════╝${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if service $service_name status | grep -q "running\|active"; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    print_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to check URL accessibility
check_url() {
    local url=$1
    local service_name=$2
    local max_attempts=15
    local attempt=1
    
    print_status "Checking $service_name accessibility..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
            print_success "$service_name is accessible at $url"
            return 0
        fi
        
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    print_warning "$service_name may not be fully ready yet at $url"
    return 1
}

# Main setup function
main() {
    print_header
    
    # Check if running as root or with sudo access
    if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
        print_error "This script requires sudo access. Please run with sudo or ensure sudo is configured."
        exit 1
    fi
    
    # Step 1: System Dependencies Check
    print_status "Checking system dependencies..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js and yarn
    if ! command_exists node; then
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    if ! command_exists yarn; then
        print_status "Installing yarn..."
        npm install -g yarn
    fi
    
    # Check MongoDB
    if ! command_exists mongod; then
        print_error "MongoDB is required but not installed"
        exit 1
    fi
    
    print_success "System dependencies verified"
    
    # Step 2: Install Python Dependencies
    print_status "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "/root/.venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv /root/.venv
    fi
    
    # Activate virtual environment and install dependencies
    source /root/.venv/bin/activate
    pip install -r /app/backend/requirements.txt
    print_success "Python dependencies installed"
    
    # Step 3: Install Node.js Dependencies
    print_status "Installing Node.js dependencies..."
    cd /app/frontend
    yarn install
    print_success "Node.js dependencies installed"
    cd /app
    
    # Step 4: MongoDB Setup
    print_status "Setting up MongoDB..."
    
    # Start MongoDB service
    sudo service mongod start 2>/dev/null || sudo service mongodb start 2>/dev/null || true
    sleep 5
    
    # Wait for MongoDB to be ready
    local mongo_ready=false
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for MongoDB to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if mongosh --eval "db.runCommand('ping')" --quiet 2>/dev/null || mongo --eval "db.runCommand('ping')" --quiet 2>/dev/null; then
            mongo_ready=true
            print_success "MongoDB is ready!"
            break
        fi
        
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    if [ "$mongo_ready" = false ]; then
        print_error "MongoDB failed to start properly"
        exit 1
    fi
    
    # Create database and seed data
    print_status "Creating database and seeding test data..."
    python3 /app/db_setup.py
    print_success "Database setup completed"
    
    # Step 5: Start Backend Service
    print_status "Starting backend service..."
    
    # Kill any existing backend process
    pkill -f "uvicorn.*backend.server" 2>/dev/null || true
    sleep 2
    
    # Start backend in background
    cd /app
    source /root/.venv/bin/activate
    nohup uvicorn backend.server:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    sleep 5
    
    # Check if backend is running
    if ps -p $BACKEND_PID > /dev/null; then
        print_success "Backend service started (PID: $BACKEND_PID)"
    else
        print_error "Backend service failed to start"
        cat /tmp/backend.log
        exit 1
    fi
    
    # Step 6: Start Frontend Service
    print_status "Starting frontend service..."
    sudo supervisorctl start frontend 2>/dev/null || true
    sleep 5
    wait_for_service "frontend"
    
    # Step 7: Health Checks
    print_status "Performing health checks..."
    
    # Check backend health
    sleep 5
    check_url "http://localhost:8001/api/health" "Backend API"
    
    # Check frontend accessibility
    sleep 5
    check_url "http://localhost:3000" "Frontend Application"
    
    # Step 8: Final Status Report
    print_header
    print_success "🎉 AI Email Responder Setup Complete!"
    echo ""
    echo -e "${GREEN}📋 APPLICATION DETAILS:${NC}"
    echo -e "   Frontend URL: ${BLUE}http://localhost:3000${NC}"
    echo -e "   Backend API:  ${BLUE}http://localhost:8001${NC}"
    echo -e "   API Health:   ${BLUE}http://localhost:8001/api/health${NC}"
    echo ""
    echo -e "${GREEN}🔐 TEST USER CREDENTIALS:${NC}"
    echo -e "   Username: ${YELLOW}testuser${NC}"
    echo -e "   Password: ${YELLOW}testpass123${NC}"
    echo -e "   Email:    ${YELLOW}test@example.com${NC}"
    echo ""
    echo -e "${GREEN}🗄️ DATABASE INFORMATION:${NC}"
    echo -e "   Database: ${YELLOW}email_responder${NC}"
    echo -e "   MongoDB:  ${YELLOW}mongodb://localhost:27017${NC}"
    echo ""
    echo -e "${GREEN}🚀 SERVICES STATUS:${NC}"
    sudo supervisorctl status | grep -E "(backend|frontend|mongodb)" | while read line; do
        echo -e "   $line"
    done
    echo ""
    echo -e "${GREEN}🎯 QUICK START:${NC}"
    echo -e "   1. Open browser to: ${BLUE}http://localhost:3000${NC}"
    echo -e "   2. Login with: ${YELLOW}testuser / testpass123${NC}"
    echo -e "   3. Explore the dashboard and features!"
    echo ""
    echo -e "${GREEN}🛠️ DEVELOPMENT COMMANDS:${NC}"
    echo -e "   Restart all services: ${BLUE}sudo supervisorctl restart all${NC}"
    echo -e "   Check service status: ${BLUE}sudo supervisorctl status${NC}"
    echo -e "   View backend logs:    ${BLUE}sudo tail -f /var/log/supervisor/backend.out.log${NC}"
    echo -e "   View frontend logs:   ${BLUE}sudo tail -f /var/log/supervisor/frontend.out.log${NC}"
    echo ""
    print_success "Setup completed successfully! 🎉"
}

# Run main function
main "$@"