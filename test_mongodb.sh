#!/bin/bash

# MongoDB Installation Test Script
# This script tests if MongoDB can be installed and started

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

print_status "Testing MongoDB installation and startup..."

# Check if MongoDB is installed
if command -v mongod >/dev/null 2>&1; then
    print_success "MongoDB is installed"
    
    # Check version
    mongod_version=$(mongod --version | head -1)
    print_status "MongoDB version: $mongod_version"
    
    # Test if MongoDB can start
    print_status "Testing MongoDB startup..."
    
    # Try multiple startup methods
    if sudo systemctl start mongod 2>/dev/null; then
        print_success "MongoDB started using systemd"
        mongo_started=true
    elif sudo service mongod start 2>/dev/null; then
        print_success "MongoDB started using service command"
        mongo_started=true
    elif sudo service mongodb start 2>/dev/null; then
        print_success "MongoDB started using mongodb service"
        mongo_started=true
    else
        print_status "Trying to start MongoDB directly..."
        sudo mkdir -p /data/db
        sudo chown -R $(whoami) /data/db
        mongod --dbpath /data/db --fork --logpath /tmp/mongod.log --bind_ip_all 2>/dev/null
        if [ $? -eq 0 ]; then
            print_success "MongoDB started directly"
            mongo_started=true
        else
            print_error "Failed to start MongoDB"
            mongo_started=false
        fi
    fi
    
    # Test connection
    if [ "$mongo_started" = true ]; then
        sleep 3
        print_status "Testing MongoDB connection..."
        
        if mongosh --eval "db.runCommand('ping')" --quiet 2>/dev/null; then
            print_success "MongoDB connection test passed (mongosh)"
        elif mongo --eval "db.runCommand('ping')" --quiet 2>/dev/null; then
            print_success "MongoDB connection test passed (mongo)"
        else
            print_error "MongoDB connection test failed"
        fi
    fi
else
    print_error "MongoDB is not installed"
    print_status "MongoDB installation would be required"
fi

print_status "Test completed"