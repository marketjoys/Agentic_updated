#!/bin/bash

# Quick test of the database setup portion
echo "Testing database setup portion of setup script..."

cd /app

# Test Python path
echo "Testing Python path..."
if [ -f "/root/.venv/bin/python3" ]; then
    echo "✅ Python virtual environment found"
    /root/.venv/bin/python3 --version
else
    echo "❌ Python virtual environment not found"
    exit 1
fi

# Test database setup script
echo "Testing database setup script..."
if [ -f "db_setup.py" ]; then
    echo "✅ Database setup script found"
    /root/.venv/bin/python3 db_setup.py
else
    echo "❌ Database setup script not found"
    exit 1
fi

echo "✅ Database setup test completed successfully!"