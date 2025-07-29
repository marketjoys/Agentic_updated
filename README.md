# AI Email Responder

A comprehensive AI-driven email responder system built with React frontend, FastAPI backend, and MongoDB database.

## 🏗️ Project Structure

```
/app/
├── backend/                    # FastAPI backend application
│   ├── app/                   # Application modules
│   ├── server.py              # Main FastAPI server
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/                   # React frontend application
│   ├── src/                   # React source code
│   ├── public/                # Static assets
│   ├── package.json          # Node.js dependencies
│   └── build/                # Production build
├── tests/                     # All testing files
│   ├── backend/              # Backend-specific tests
│   │   ├── test_app.py
│   │   ├── test_auto_responder.py
│   │   └── ...
│   ├── *_test.py             # Main test files
│   ├── test_*.sh             # Shell test scripts
│   └── *.json                # Test results
├── scripts/                   # Utility and setup scripts
│   ├── db_setup.py           # Database setup
│   ├── setup.sh              # Environment setup
│   ├── manage.sh             # Management utilities
│   └── ...
├── docs/                      # Documentation files
│   ├── README.md             # Project documentation
│   ├── SETUP_GUIDE.md        # Setup instructions
│   ├── FEATURE_LIST.md       # Feature documentation
│   └── ...
└── test_result.md            # Main testing protocol
```

## 📂 Directory Details

### `/backend/`
Core FastAPI application with clean structure:
- `server.py` - Main application server
- `app/` - Application modules and routes
- `requirements.txt` - Python dependencies
- `.env` - Environment configuration

### `/frontend/`
React application with modern setup:
- `src/` - React components and logic
- `public/` - Static assets and HTML
- `package.json` - Node.js dependencies
- `build/` - Production build output

### `/tests/`
All testing files organized by category:
- 52 Python test files
- Backend-specific tests in `backend/` subdirectory
- Shell scripts for database testing
- JSON test results and artifacts

### `/scripts/`
Utility and setup scripts:
- Database setup and seeding
- Email provider configuration
- Environment setup scripts
- Management utilities

### `/docs/`
Comprehensive documentation:
- Setup and configuration guides
- Feature documentation
- Executive summaries
- Screenshots and visual assets

## 🚀 Key Features

- **AI-Powered Email Responses**: Intelligent email classification and auto-responses
- **Campaign Management**: Create and manage email campaigns
- **Prospect Management**: Handle prospect data and lists
- **Template System**: Customizable email templates
- **Auto-Responder**: Automated email monitoring and responses
- **Voice Recognition**: Voice-enabled interface
- **Dashboard Analytics**: Real-time campaign analytics

## 🔧 Technologies Used

- **Backend**: FastAPI, Python, MongoDB
- **Frontend**: React, Tailwind CSS, JavaScript
- **AI**: Groq AI for email classification
- **Database**: MongoDB with proper indexing
- **Email**: SMTP/IMAP integration
- **Testing**: Comprehensive test suite

## 📋 Setup Instructions

Refer to `/docs/SETUP_GUIDE.md` for detailed setup instructions.

## 🧪 Testing

All tests are organized in the `/tests/` directory. Run the main test suite:

```bash
# Backend tests
python tests/comprehensive_backend_test.py

# Frontend tests
# See individual test files in /tests/
```

## 📊 Production Status

The system is production-ready with:
- ✅ Full backend API functionality
- ✅ Complete frontend interface
- ✅ AI email classification
- ✅ Auto-responder system
- ✅ Campaign management
- ✅ Real Gmail integration

For detailed testing results, see `test_result.md` in the root directory.