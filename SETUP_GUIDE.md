# AI Email Responder - Quick Setup Guide

## One-Command Setup 🚀

Run the complete setup with a single command:

```bash
./setup.sh
```

This script will:

1. ✅ **Check system dependencies** (Python, Node.js, MongoDB)
2. 🐍 **Install Python dependencies** (FastAPI, MongoDB drivers, AI libraries)
3. 🌟 **Install Node.js dependencies** (React, Tailwind, Axios)
4. 🗄️ **Setup MongoDB database** with test data
5. 👤 **Create test user account** (testuser/testpass123)
6. 🚀 **Start all services** (Backend, Frontend, MongoDB)
7. 🔍 **Perform health checks** and display status

## Access Information

After setup completes, you can access:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Health Check**: http://localhost:8001/api/health

## Test User Credentials

- **Username**: `testuser`
- **Password**: `testpass123`
- **Email**: `test@example.com`

## Service Management

Use the included management script for easy service control:

```bash
# Start all services
./manage.sh start

# Stop all services  
./manage.sh stop

# Check service status
./manage.sh status

# Restart all services
./manage.sh restart
```

## Manual Service Commands

If you need to manage services manually:

```bash
# Check what's running
ps aux | grep uvicorn     # Backend
ps aux | grep yarn        # Frontend

# Stop services
pkill -f 'uvicorn.*backend.server'  # Stop backend
pkill -f 'yarn.*start'             # Stop frontend

# View logs
tail -f /tmp/backend.log   # Backend logs
tail -f /tmp/frontend.log  # Frontend logs
```

## Database Information

- **Database Name**: `email_responder`
- **MongoDB URL**: `mongodb://localhost:27017`
- **Collections**: users, prospects, templates, campaigns, intents, lists, email_providers

## Sample Data Included

The setup automatically creates:
- 1 test user account
- 5 sample prospects
- 4 email templates
- 2 sample campaigns
- 4 intent configurations
- 4 prospect lists
- 2 email providers

## Troubleshooting

If setup fails:

1. **Check logs**: `tail -f /tmp/backend.log` or `tail -f /tmp/frontend.log`
2. **Verify ports**: Make sure ports 3000 and 8001 are available
3. **Check MongoDB**: Ensure MongoDB service is running
4. **Re-run setup**: The script is idempotent - safe to run multiple times

## Features Available

Once setup is complete, you can:

- 📊 **View Dashboard** with real-time metrics
- 👥 **Manage Prospects** and contact lists
- 📧 **Create Email Templates** with variables
- 🚀 **Launch Campaigns** with scheduling
- 🤖 **Configure AI Intent Detection** 
- 📈 **View Analytics** and performance metrics
- ⚙️ **Manage Email Providers** (Gmail, Outlook)

## Quick Start

1. Run `./setup.sh` and wait for completion
2. Open browser to http://localhost:3000
3. Login with `testuser` / `testpass123`
4. Explore the dashboard and features!

---

*The AI Email Responder is powered by Groq AI and includes comprehensive email campaign management, intent detection, and automated response capabilities.*