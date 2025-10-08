# TypeFace Finance Assistant - Setup Guide

A comprehensive guide to setting up and running the TypeFace Finance Assistant application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software

1. **Python 3.12+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version` or `python3 --version`

2. **Node.js 18+ and npm**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify installation: `node --version` and `npm --version`

3. **Git**
   - Download from [git-scm.com](https://git-scm.com/)
   - Verify installation: `git --version`

4. **Ghostscript** (Required for PDF processing)
   - **macOS**: `brew install ghostscript`
   - **Ubuntu/Debian**: `sudo apt-get install ghostscript`
   - **Windows**: Download from [ghostscript.com](https://www.ghostscript.com/download/gsdnld.html)

5. **Tesseract OCR** (Required for receipt scanning)
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **Windows**: Download from [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

### API Keys

You'll need a **Google Gemini API Key** for AI-powered features:
- Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ThinkyMiner/TypeFace-Finance-Assistant.git
cd TypeFace-Finance-Assistant
```

### 2. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
cd backend
```

#### Create a Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: If you encounter issues with `camelot-py`, you may need to install additional dependencies:
- **macOS**: `brew install tk-tcl`
- **Ubuntu/Debian**: `sudo apt-get install python3-tk python3-dev`

### 3. Frontend Setup

Open a new terminal window/tab and navigate to the frontend directory:

```bash
cd frontend
npm install
```

---

## Configuration

### Backend Configuration

1. **Create Environment File**

   Create a `.env` file in the `backend` directory:

   ```bash
   cd backend
   touch .env
   ```

2. **Add Environment Variables**

   Open `.env` and add the following:

   ```env
   # Database
   DATABASE_URL=sqlite:///./finance.db

   # Security
   SECRET_KEY=your-secret-key-here-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Google Gemini API (Required for AI features)
   GEMINI_API_KEY=your-gemini-api-key-here

   # CORS Settings
   ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

   **Important**:
   - Replace `your-gemini-api-key-here` with your actual Gemini API key
   - Generate a strong secret key for production:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```

3. **Initialize the Database**

   The database will be automatically created when you first run the backend. To manually initialize:

   ```bash
   # Make sure you're in the backend directory with venv activated
   python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)""
   ```

### Frontend Configuration

The frontend is pre-configured to connect to `http://localhost:8000` (backend API).

If you need to change the backend URL, edit `frontend/src/api/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

---

## Running the Application

You'll need **two terminal windows** - one for the backend and one for the frontend.

### Terminal 1: Start the Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if not already activated)
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Run the FastAPI server
python -m uvicorn app.main:app --reload
```

The backend will start at: **http://localhost:8000**

API documentation available at:
- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

### Terminal 2: Start the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Start the React development server
npm start
```

The frontend will automatically open at: **http://localhost:3000**

---

## Using the Application

### First Time Setup

1. **Create an Account**
   - Open http://localhost:3000
   - Click "Sign Up"
   - Enter your details and create an account

2. **Login**
   - Use your credentials to log in

3. **Start Managing Finances**
   - Add transactions manually
   - Upload receipts (images/PDFs) for automatic extraction
   - Import bank statements (any PDF format supported via AI)
   - View analytics and insights

### Key Features

#### 📸 Receipt Scanning
- Upload receipt images (JPG, PNG) or PDFs
- AI automatically extracts amount, merchant, date
- Review and confirm before saving

#### 📄 Bank Statement Import
- Upload any bank statement PDF (works with any format!)
- Gemini AI intelligently extracts all transactions
- Automatically classifies income vs expenses
- Preview before importing

#### 📊 Dashboard & Analytics
- View transaction history
- Filter by date, category, type
- See spending trends and insights

#### 📤 Export Data
- Export transactions to PDF
- Export to CSV for analysis

---

## Troubleshooting

### Common Issues

#### 1. **"Module not found" errors in Python**

**Solution**: Make sure your virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 2. **"Cannot connect to backend" in frontend**

**Solutions**:
- Ensure backend is running on port 8000
- Check if backend URL in `frontend/src/api/api.js` is correct
- Verify CORS settings in `backend/.env`

#### 3. **PDF import fails with "No tables found"**

**Solutions**:
- Ensure Ghostscript is installed: `gs --version`
- Check if GEMINI_API_KEY is set in backend/.env
- Verify the PDF contains text (not scanned images)

#### 4. **Receipt scanning not working**

**Solutions**:
- Ensure Tesseract OCR is installed: `tesseract --version`
- Check if GEMINI_API_KEY is set for better accuracy
- Try with a clearer image

#### 5. **Database errors**

**Solution**: Delete the database and reinitialize:
```bash
cd backend
rm finance.db
python -c "from app.db import init_db; init_db()"
```

#### 6. **Port already in use**

**Backend (8000)**:
```bash
# Find and kill process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Frontend (3000)**:
```bash
# macOS/Linux:
lsof -ti:3000 | xargs kill -9
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

## Development Tips

### Backend Hot Reload
The `--reload` flag enables automatic restart when code changes are detected.

### Frontend Hot Reload
React dev server automatically refreshes on code changes.

### Viewing Logs

**Backend logs**: Displayed in the terminal running uvicorn

**Frontend logs**: Check browser console (F12 → Console tab)

### Testing API Endpoints

Use the Swagger UI at http://localhost:8000/docs to test API endpoints interactively.

---

## Production Deployment

For production deployment:

1. **Update Security Settings**
   - Generate strong SECRET_KEY
   - Set proper ALLOWED_ORIGINS
   - Use production database (PostgreSQL recommended)

2. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

3. **Serve Backend with Production ASGI Server**
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

4. **Use Environment Variables**
   - Never commit .env files
   - Use platform-specific secrets management

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/ThinkyMiner/TypeFace-Finance-Assistant/issues)
- **Documentation**: See [README.md](README.md) for feature overview

---

## License

This project is open source and available under the MIT License.

---

**Happy Tracking! 💰**
