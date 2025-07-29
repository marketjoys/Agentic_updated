# AI Email Responder - Windows Setup Guide

## Prerequisites

1. **Python 3.11+** - Download from [python.org](https://python.org)
2. **Node.js 18+** - Download from [nodejs.org](https://nodejs.org)  
3. **MongoDB** - Either:
   - Install MongoDB Community Server locally, OR
   - Use MongoDB Atlas (cloud database)
4. **Git** - Download from [git-scm.com](https://git-scm.com)

## Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd ai-email-responder
```

## Step 2: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```bash
   # On Windows Command Prompt
   venv\Scripts\activate
   
   # On Windows PowerShell
   venv\Scripts\Activate.ps1
   
   # On Git Bash (recommended)
   source venv/Scripts/activate
   ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables:**
   - Copy `.env` file and update the following:
   ```env
   MONGO_URL=mongodb://localhost:27017/email_responder
   GROQ_API_KEY=your_groq_api_key_here
   JWT_SECRET_KEY=your-secret-key-here
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   IMAP_HOST=imap.gmail.com
   IMAP_PORT=993
   ```

6. **Start the backend server:**
   ```bash
   python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

## Step 3: Frontend Setup

1. **Open a new terminal and navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   # OR
   yarn install
   ```

3. **Configure environment variables:**
   - Update `frontend/.env`:
   ```env
   REACT_APP_BACKEND_URL=http://localhost:8001
   ```

4. **Start the frontend development server:**
   ```bash
   npm start
   # OR  
   yarn start
   ```

## Step 4: Database Setup

### Option A: Local MongoDB
1. Start MongoDB service on Windows
2. Database will be created automatically when first accessed

### Option B: MongoDB Atlas (Cloud)
1. Create account at [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create a new cluster
3. Get connection string and update `MONGO_URL` in `.env`

## Step 5: API Keys Setup

### GROQ API Key (Required for AI functionality)
1. Visit [console.groq.com](https://console.groq.com)
2. Create account and generate API key
3. Add to `GROQ_API_KEY` in `.env`

### Gmail App Password (Required for email sending)
1. Enable 2FA on your Gmail account
2. Generate App Password: [support.google.com/accounts/answer/185833](https://support.google.com/accounts/answer/185833)
3. Add to `SMTP_PASSWORD` in `.env`

## Step 6: Access the Application

1. **Frontend:** http://localhost:3000
2. **Backend API:** http://localhost:8001
3. **API Documentation:** http://localhost:8001/docs

## Default Login Credentials

- **Username:** `testuser`
- **Password:** `testpass123`

## Troubleshooting

### Common Issues:

1. **Port already in use:**
   - Change ports in the startup commands
   - Kill existing processes using the ports

2. **MongoDB connection error:**
   - Ensure MongoDB is running
   - Check connection string in `.env`

3. **CORS errors:**
   - Ensure `REACT_APP_BACKEND_URL` points to correct backend URL
   - Check that both frontend and backend are running

4. **Python dependencies fail:**
   - Ensure you're using Python 3.11+
   - Try upgrading pip: `python -m pip install --upgrade pip`

5. **Node.js dependencies fail:**
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install` again

## Production Deployment

For production deployment, you'll need to:

1. Set up a production MongoDB instance
2. Configure production environment variables
3. Build the frontend: `npm run build`
4. Use a production WSGI server like Gunicorn for the backend
5. Set up reverse proxy (nginx) for serving static files and routing

## Support

If you encounter issues:
1. Check the backend logs for error messages
2. Check browser developer console for frontend errors
3. Ensure all environment variables are correctly set
4. Verify all services (MongoDB, backend, frontend) are running

## Features Available

✅ **Campaign Creation & Management** - Create and manage email campaigns
✅ **Intent Configuration** - Set up auto-response intents (8 available)
✅ **Auto Responders** - Automatic email responses based on AI intent detection
✅ **Prospect Management** - Manage email prospects and lists
✅ **Template System** - Create and manage email templates
✅ **Analytics** - Track campaign performance
✅ **AI Agent** - Natural language campaign management
✅ **Real-time Monitoring** - Monitor email processing and follow-ups

The system is fully functional and ready for production use!