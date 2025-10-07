# TypeFace - Personal Finance Tracker

A comprehensive personal finance management application with AI-powered insights, receipt scanning, and bank statement import capabilities. Built with a modern tech stack featuring FastAPI backend and React frontend.

![TypeFace](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![React](https://img.shields.io/badge/React-19.2-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Core Services & Implementation](#core-services--implementation)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Usage Guide](#usage-guide)

---

## Overview

TypeFace is a full-stack personal finance tracker that helps users manage their income and expenses with modern features including:

- **Transaction Management**: Track income and expenses with detailed categorization
- **AI Assistant**: Get financial insights and recommendations powered by Google Gemini AI
- **Receipt Scanner**: Extract transaction data from receipt images using OCR (Tesseract)
- **Bank Statement Import**: Import transactions from PDF bank statements using advanced parsing
- **PDF Export**: Generate detailed transaction reports in PDF format
- **Data Visualization**: Interactive charts showing spending patterns and trends
- **User Authentication**: Secure JWT-based authentication system

---

## Architecture

TypeFace follows a **modern client-server architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                       FRONTEND (React)                       │
│  ┌─────────────┬──────────────┬────────────┬──────────────┐ │
│  │  Dashboard  │ AI Assistant │  Receipt   │   Auth       │ │
│  │             │              │  Scanner   │   Pages      │ │
│  └─────────────┴──────────────┴────────────┴──────────────┘ │
│                      React Router DOM                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         │ (Port 3000 → 8000)
┌────────────────────────▼────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Layer (v1)                          │   │
│  │  ┌──────┬─────────┬──────────┬──────────┬─────────┐ │   │
│  │  │ Auth │ Txns    │ Receipts │ Imports  │ AI      │ │   │
│  │  └──────┴─────────┴──────────┴──────────┴─────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Business Logic & Services                  │   │
│  │  ┌─────────────┬──────────────┬──────────────────┐  │   │
│  │  │ Statement   │ Receipt      │ AI Assistant     │  │   │
│  │  │ Parser      │ Scanner      │ Service          │  │   │
│  │  └─────────────┴──────────────┴──────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Data Layer (SQLAlchemy ORM)                  │   │
│  │  ┌──────────┬─────────────┬──────────────────────┐  │   │
│  │  │ User     │ Transaction │ Category             │  │   │
│  │  │ Model    │ Model       │ Model                │  │   │
│  │  └──────────┴─────────────┴──────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    SQLite Database                           │
│  ┌──────────┬─────────────┬──────────────────────┐         │
│  │ users    │ transactions│ categories           │         │
│  └──────────┴─────────────┴──────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **Layered Architecture**: Clear separation between presentation, business logic, and data layers
2. **RESTful API Design**: Stateless HTTP endpoints following REST conventions
3. **JWT Authentication**: Secure token-based authentication with Bearer tokens
4. **ORM Pattern**: SQLAlchemy for database abstraction and migrations
5. **Service Layer**: Business logic encapsulated in reusable services
6. **Component-Based Frontend**: Modular React components with hooks

---

## Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | Latest | High-performance async web framework |
| **Python** | 3.12+ | Primary backend language |
| **SQLAlchemy** | 2.0+ | ORM and database toolkit |
| **Alembic** | Latest | Database migration tool |
| **Pydantic** | 2.0+ | Data validation and settings |
| **PyJWT** | Latest | JWT token generation and validation |
| **Passlib** | Latest | Password hashing with bcrypt |
| **Uvicorn** | Latest | ASGI server |
| **SQLite** | 3 | Development database (PostgreSQL for production) |

#### AI & ML Libraries

| Library | Purpose |
|---------|---------|
| **Google Generative AI** | AI-powered financial insights (Gemini) |
| **Tesseract OCR** | Receipt text extraction |
| **OpenCV** | Image preprocessing |
| **Pillow** | Image manipulation |

#### Document Processing

| Library | Purpose |
|---------|---------|
| **PyMuPDF (fitz)** | PDF text extraction |
| **PDFPlumber** | Structured PDF data extraction |
| **Camelot** | PDF table extraction |
| **Pandas** | Data manipulation and analysis |
| **ReportLab** | PDF generation for exports |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2 | UI library |
| **React Router DOM** | 7.9+ | Client-side routing |
| **Chart.js** | 4.5+ | Data visualization |
| **react-chartjs-2** | 5.3+ | React wrapper for Chart.js |
| **React Scripts** | 5.0 | Build tooling (CRA) |

### Development Tools

- **Git**: Version control
- **Alembic**: Database migrations
- **Python venv**: Virtual environment management
- **npm**: Frontend package management

---

## Features

### 1. **User Authentication & Authorization**

- Secure registration and login system
- JWT-based stateless authentication
- Password hashing with bcrypt
- Protected routes and API endpoints

**Implementation**:
- Backend: [app/api/v1/auth.py](backend/app/api/v1/auth.py)
- Frontend: [src/components/Login.js](frontend/src/components/Login.js), [src/components/Register.js](frontend/src/components/Register.js)

### 2. **Transaction Management**

- Add, view, and filter transactions
- Support for income and expense types
- Categorization with merchant information
- Date-based filtering
- Pagination for large datasets
- Real-time statistics (total income, expenses, balance)

**Implementation**:
- Backend: [app/api/v1/transactions.py](backend/app/api/v1/transactions.py)
- Models: [app/models/transaction.py](backend/app/models/transaction.py)
- Frontend: [src/components/Dashboard.js](frontend/src/components/Dashboard.js)

### 3. **AI Financial Assistant**

Powered by **Google Gemini AI**, providing:

- **Financial Overview**: Comprehensive analysis of your financial health
- **Spending Analysis**: Identify where money is being spent
- **Trend Detection**: Discover spending patterns over time
- **Custom Queries**: Ask natural language questions about your finances
- **Visual Charts**: Interactive spending breakdowns
- **Smart Recommendations**: Personalized financial advice

**Implementation**:
- Service: [app/services/ai_assistant.py](backend/app/services/ai_assistant.py)
- API: [app/api/v1/ai_assistant.py](backend/app/api/v1/ai_assistant.py)
- Frontend: [src/components/AIAssistant.js](frontend/src/components/AIAssistant.js)

**How it works**:
1. User asks a question or selects a preset query
2. System fetches user's transaction history
3. Transaction data is sent to Gemini AI with structured prompts
4. AI analyzes patterns and generates insights
5. Response includes text insights, chart data (if applicable), and recommendations

### 4. **Receipt Scanner (OCR)**

Extract transaction details from receipt images:

- Upload receipt photos (JPG, PNG, WEBP)
- OCR text extraction using Tesseract
- AI-powered data parsing to extract:
  - Merchant name
  - Transaction amount
  - Date
  - Payment method
  - Individual items
- Automatic form pre-filling
- Image preprocessing for better accuracy

**Implementation**:
- Service: [app/services/receipt_scanner.py](backend/app/services/receipt_scanner.py)
- API: [app/api/v1/receipts.py](backend/app/api/v1/receipts.py)
- Frontend: [src/components/ReceiptScanner.js](frontend/src/components/ReceiptScanner.js)

**Processing Pipeline**:
```
Receipt Image → Image Preprocessing → OCR (Tesseract) → AI Parsing (Gemini) → Structured Data
```

### 5. **Bank Statement Import**

Import transactions from PDF bank statements:

- Support for multiple PDF formats
- Multiple parsing methods:
  - **Text-based extraction** (PyMuPDF)
  - **Table extraction** (Camelot, PDFPlumber)
  - **AI-powered parsing** (Gemini for complex formats)
- Fallback mechanism for best results
- Duplicate detection
- Preview before import
- Batch transaction creation

**Implementation**:
- Service: [app/services/statement_parser.py](backend/app/services/statement_parser.py)
- API: [app/api/v1/imports.py](backend/app/api/v1/imports.py)
- Frontend: Import Modal in [src/components/Dashboard.js](frontend/src/components/Dashboard.js)

**Parsing Strategy**:
```
PDF Upload → Method 1 (Text) → Success? → Preview
                ↓ Fail
           Method 2 (Tables) → Success? → Preview
                ↓ Fail
           Method 3 (AI) → Preview
```

### 6. **PDF Export**

Generate professional transaction reports:

- Export filtered transactions to PDF
- Customizable date ranges
- Transaction type filtering (income/expense/all)
- Professional formatting with headers and tables
- Automatic file download

**Implementation**:
- PDF Generation: [app/api/v1/transactions.py](backend/app/api/v1/transactions.py) (`export_transactions_pdf` endpoint)
- Uses ReportLab for PDF creation

### 7. **Data Visualization**

Interactive charts powered by Chart.js:

- **Pie Charts**: Spending breakdown by category/merchant
- **Line Charts**: Spending trends over time
- **Bar Charts**: Category comparisons
- Dynamic chart generation based on AI analysis

**Implementation**:
- Chart Component: [src/components/ChartRenderer.js](frontend/src/components/ChartRenderer.js)
- Chart.js integration with react-chartjs-2

### 8. **Categories**

Organize transactions with categories:

- Pre-defined categories (Food, Transport, Entertainment, etc.)
- User-customizable categories
- Category-based filtering and analysis

**Implementation**:
- Backend: [app/api/v1/categories.py](backend/app/api/v1/categories.py)
- Models: [app/models/category.py](backend/app/models/category.py)

---

## Project Structure

```
TypeFace/
├── backend/                      # FastAPI backend application
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/              # API version 1 endpoints
│   │   │       ├── auth.py      # Authentication endpoints
│   │   │       ├── transactions.py  # Transaction CRUD + PDF export
│   │   │       ├── receipts.py  # Receipt scanning endpoint
│   │   │       ├── imports.py   # Bank statement import
│   │   │       ├── ai_assistant.py  # AI query endpoint
│   │   │       ├── categories.py    # Category management
│   │   │       ├── stats.py     # Statistics endpoint
│   │   │       └── health.py    # Health check
│   │   ├── core/               # Core functionality
│   │   │   ├── config.py       # Application configuration
│   │   │   └── security.py     # JWT auth & password hashing
│   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── user.py         # User model
│   │   │   ├── transaction.py  # Transaction model
│   │   │   └── category.py     # Category model
│   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── auth.py         # Auth request/response models
│   │   │   ├── transaction.py  # Transaction schemas
│   │   │   └── category.py     # Category schemas
│   │   ├── services/           # Business logic layer
│   │   │   ├── receipt_scanner.py    # OCR & receipt processing
│   │   │   ├── statement_parser.py   # PDF bank statement parsing
│   │   │   └── ai_assistant.py       # Gemini AI integration
│   │   ├── db.py              # Database connection & session
│   │   └── main.py            # FastAPI application entry point
│   ├── migrations/            # Alembic database migrations
│   ├── uploads/               # Temporary file storage
│   ├── requirements.txt       # Python dependencies
│   ├── alembic.ini           # Alembic configuration
│   ├── .env                  # Environment variables (not in git)
│   └── finance.db            # SQLite database (dev only)
│
├── frontend/                  # React frontend application
│   ├── public/               # Static files
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Dashboard.js       # Main dashboard
│   │   │   ├── Login.js          # Login page
│   │   │   ├── Register.js       # Registration page
│   │   │   ├── Landing.js        # Landing page
│   │   │   ├── AIAssistant.js    # AI chat interface
│   │   │   ├── ReceiptScanner.js # Receipt upload & scan
│   │   │   └── ChartRenderer.js  # Chart.js wrapper
│   │   ├── App.js            # Main app component & routing
│   │   ├── App.css           # Global styles
│   │   └── index.js          # React entry point
│   ├── package.json          # Node dependencies
│   └── node_modules/         # NPM packages
│
├── .gitignore               # Git ignore rules
├── .env                     # Root environment config
└── README.md               # This file
```

---

## Core Services & Implementation

### Service Layer Architecture

The backend implements a **service-oriented architecture** where complex business logic is abstracted into dedicated service modules.

### 1. Receipt Scanner Service

**File**: `backend/app/services/receipt_scanner.py`

**Purpose**: Extract structured transaction data from receipt images using OCR and AI.

**Key Components**:

```python
class ReceiptScanner:
    def preprocess_image(image_path: str) -> str:
        """
        Preprocessing steps:
        1. Load image with OpenCV
        2. Convert to grayscale
        3. Apply Gaussian blur for noise reduction
        4. Apply adaptive thresholding
        5. Sharpen the image
        Returns: Path to processed image
        """

    async def scan_receipt(image_path: str) -> dict:
        """
        1. Preprocess image
        2. Extract text using Tesseract OCR
        3. Send raw text to Gemini AI
        4. AI parses and structures the data
        Returns: {
            merchant, amount, date, payment_method,
            items, confidence, raw_text
        }
        """
```

**Technology Integration**:
- **OpenCV**: Image preprocessing and enhancement
- **Tesseract**: OCR text extraction
- **Pillow**: Image format handling
- **Google Gemini AI**: Intelligent data parsing

**Workflow**:
```
Image Upload → Preprocessing → OCR → AI Parsing → Validation → Response
```

### 2. Bank Statement Parser Service

**File**: `backend/app/services/statement_parser.py`

**Purpose**: Extract transactions from PDF bank statements using multiple parsing strategies.

**Key Components**:

```python
class StatementParser:
    async def parse_statement(pdf_path: str, user_id: int) -> dict:
        """
        Orchestrates parsing with fallback methods:
        1. Try text-based extraction (PyMuPDF)
        2. If failed, try table extraction (Camelot/PDFPlumber)
        3. If failed, use AI parsing (Gemini)
        Returns: {
            success, transactions[], method, message
        }
        """

    def parse_text_based(text: str) -> list:
        """
        Pattern matching for common statement formats
        Uses regex to identify transaction lines
        """

    def parse_table_based(pdf_path: str) -> list:
        """
        Extract tables using Camelot (stream/lattice)
        Fallback to PDFPlumber if Camelot fails
        """

    async def parse_with_ai(pdf_path: str) -> list:
        """
        Send PDF text to Gemini AI
        AI identifies and structures transactions
        """
```

**Parsing Methods**:

1. **Text-Based** (Fastest):
   - Extract all text from PDF
   - Use regex patterns to find transaction lines
   - Parse dates, amounts, descriptions

2. **Table-Based** (Most Accurate for tabular data):
   - Camelot: For PDFs with clear table structures
   - PDFPlumber: Fallback for complex layouts

3. **AI-Based** (Most Flexible):
   - Handles non-standard formats
   - Understands context
   - Can parse handwritten or scanned statements

**Data Validation**:
- Amount validation (must be numeric)
- Date parsing (multiple format support)
- Duplicate detection before import

### 3. AI Assistant Service

**File**: `backend/app/services/ai_assistant.py`

**Purpose**: Provide intelligent financial insights using Google Gemini AI.

**Key Components**:

```python
async def analyze_transactions_with_ai(query: str, transactions: list) -> dict:
    """
    1. Prepare transaction data summary
    2. Build AI prompt with context
    3. Send to Gemini AI
    4. Parse AI response
    5. Generate chart data if needed
    Returns: {
        insight: str,
        chart: dict | None,
        recommendations: list
    }
    """

def get_preset_insights(transactions: list, preset: str) -> dict:
    """
    Pre-configured analysis for common queries:
    - 'overview': Financial health summary
    - 'spending': Spending breakdown by category
    - 'trends': Time-based spending patterns
    """

def generate_chart_data(transactions: list, chart_type: str) -> dict:
    """
    Generate Chart.js compatible data structures:
    - Pie charts for category/merchant distribution
    - Line charts for trends over time
    - Bar charts for comparisons
    """
```

**AI Integration**:
- **Model**: Google Gemini (gemini-pro)
- **Context**: Transaction history, user query
- **Output**: Natural language insights + structured data
- **Safety**: Content filtering, error handling

**Prompt Engineering**:
```python
prompt = f"""
You are a financial advisor AI. Analyze these transactions:

{transaction_summary}

User question: {query}

Provide:
1. Clear insights in 2-3 sentences
2. Chart data (if visualization helps)
3. 3-5 actionable recommendations
"""
```

### 4. Authentication & Security

**File**: `backend/app/core/security.py`

**Key Components**:

```python
def hash_password(password: str) -> str:
    """Use bcrypt to hash passwords"""

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password against hash"""

def create_access_token(data: dict) -> str:
    """Generate JWT token with expiration"""

def get_current_user_id(token: str) -> int:
    """Validate JWT and extract user ID"""
```

**Security Features**:
- Bcrypt password hashing (work factor: 12)
- JWT tokens with expiration
- Dependency injection for protected routes
- CORS configuration for frontend

---

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com
password=secure_password

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Transaction Endpoints

#### Get Transactions (Paginated)
```http
GET /transactions?limit=10&offset=0&start_date=2024-01-01&end_date=2024-12-31&kind=expense
Authorization: Bearer {token}

Response: 200 OK
Headers: X-Total-Count: 150
[
  {
    "id": 1,
    "kind": "expense",
    "amount": 45.50,
    "occurred_on": "2024-10-01",
    "merchant": "Starbucks",
    "note": "Morning coffee",
    "payment_method": "Credit Card",
    "category_id": 2
  }
]
```

#### Create Transaction
```http
POST /transactions
Authorization: Bearer {token}
Content-Type: application/json

{
  "kind": "expense",
  "amount": 45.50,
  "occurred_on": "2024-10-01",
  "merchant": "Starbucks",
  "note": "Morning coffee",
  "payment_method": "Credit Card"
}

Response: 201 Created
```

#### Export Transactions to PDF
```http
GET /transactions/export/pdf?start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer {token}

Response: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="transactions.pdf"
```

### Receipt Scanner

#### Scan Receipt
```http
POST /receipts/scan
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [receipt_image.jpg]

Response: 200 OK
{
  "merchant": "Whole Foods",
  "amount": 78.45,
  "date": "2024-10-07",
  "payment_method": "Credit Card",
  "items": ["Milk", "Bread", "Eggs"],
  "confidence": 0.92,
  "raw_text": "WHOLE FOODS MARKET..."
}
```

### Bank Statement Import

#### Upload Statement (Preview)
```http
POST /imports/bank-statement
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [statement.pdf]

Response: 200 OK
{
  "preview": [...10 transactions...],
  "total_count": 45,
  "method": "text_based",
  "message": "Preview ready. Found 45 transactions."
}
```

#### Confirm Import
```http
POST /imports/confirm
Authorization: Bearer {token}

Response: 200 OK
[...all imported transactions...]
```

### AI Assistant

#### Query AI
```http
POST /ai/query
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "Where am I spending the most?",
  "preset": "spending"
}

Response: 200 OK
{
  "insight": "Your top spending category is Food & Dining at $450, followed by Transportation at $230...",
  "chart": {
    "type": "pie",
    "data": {
      "labels": ["Food", "Transport", "Entertainment"],
      "datasets": [...]
    }
  },
  "recommendations": [
    "Consider meal prepping to reduce dining costs",
    "Use public transport for commuting",
    "Set a monthly budget for entertainment"
  ]
}
```

#### Get Suggestions
```http
GET /ai/suggestions
Authorization: Bearer {token}

Response: 200 OK
{
  "suggestions": [
    {"text": "How am I doing financially?", "preset": "overview"},
    {"text": "Where am I spending the most?", "preset": "spending"},
    ...
  ]
}
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    kind VARCHAR(50) NOT NULL,  -- 'income' or 'expense'
    amount DECIMAL(10, 2) NOT NULL,
    occurred_on DATE NOT NULL,
    merchant VARCHAR(255),
    note TEXT,
    payment_method VARCHAR(100),
    category_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

### Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    user_id INTEGER,  -- NULL for system categories
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Setup Instructions

### Prerequisites

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and npm ([Download](https://nodejs.org/))
- **Tesseract OCR** (for receipt scanning)
  - macOS: `brew install tesseract`
  - Ubuntu: `sudo apt-get install tesseract-ocr`
  - Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)
- **Git** ([Download](https://git-scm.com/))
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/TypeFace.git
cd TypeFace
```

### 2. Backend Setup

#### Step 1: Create Virtual Environment

```bash
cd backend
python -m venv .venv
```

#### Step 2: Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Application
APP_NAME=Personal Finance API
ENV=dev

# Database
DATABASE_URL=sqlite:///./finance.db

# Security
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Google Gemini AI
GOOGLE_API_KEY=your-gemini-api-key-here

# Tesseract (optional, if not in PATH)
TESSERACT_CMD=/usr/local/bin/tesseract
```

**Generate a secure JWT secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Step 5: Initialize Database

```bash
# Run migrations
alembic upgrade head

# Or let FastAPI create tables automatically (dev only)
# Tables are auto-created on first run via main.py
```

#### Step 6: Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be running at: `http://localhost:8000`

**API Documentation (Swagger)**: `http://localhost:8000/docs`

### 3. Frontend Setup

Open a new terminal window:

#### Step 1: Navigate to Frontend

```bash
cd frontend
```

#### Step 2: Install Dependencies

```bash
npm install
```

#### Step 3: Start Development Server

```bash
npm start
```

Frontend will be running at: `http://localhost:3000`

The browser should automatically open. If not, navigate to the URL manually.

### 4. Verify Installation

1. **Check Backend Health**:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   Should return: `{"status": "healthy"}`

2. **Check Frontend**:
   - Open `http://localhost:3000`
   - You should see the TypeFace landing page

3. **Test Registration**:
   - Click "Get Started"
   - Register a new account
   - Login with your credentials

### 5. Production Deployment Considerations

#### Backend (Production)

1. **Use PostgreSQL instead of SQLite**:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/typeface
   ```

2. **Set Environment to Production**:
   ```env
   ENV=production
   DEBUG=False
   ```

3. **Use HTTPS and secure JWT secret**

4. **Deploy with Gunicorn**:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

5. **Set up reverse proxy (Nginx)**

#### Frontend (Production)

1. **Build for Production**:
   ```bash
   npm run build
   ```

2. **Serve with Nginx or Deploy to Vercel/Netlify**

3. **Update API URL**:
   Create `.env.production`:
   ```env
   REACT_APP_API_URL=https://your-api-domain.com
   ```

---

## Environment Variables

### Backend (.env)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | SQLAlchemy database URL | Yes | `sqlite:///./finance.db` |
| `JWT_SECRET` | Secret key for JWT signing | Yes | - |
| `JWT_ALGORITHM` | JWT algorithm | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | No | `43200` (30 days) |
| `GOOGLE_API_KEY` | Google Gemini API key | Yes (for AI features) | - |
| `TESSERACT_CMD` | Path to Tesseract executable | No | Auto-detected |
| `ENV` | Environment (dev/production) | No | `dev` |

### Frontend (.env)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `REACT_APP_API_URL` | Backend API URL | No | `http://localhost:8000` |

---

## Usage Guide

### 1. Getting Started

1. **Register an Account**:
   - Navigate to the landing page
   - Click "Get Started"
   - Fill in your details and create an account

2. **Login**:
   - Use your email and password to login
   - You'll be redirected to the dashboard

### 2. Managing Transactions

#### Add Transactions Manually
1. Fill out the "Add Transaction" form
2. Select type (Income/Expense)
3. Enter amount, date, merchant, and optional details
4. Click "Add Transaction"

#### Import from Receipt
1. Scroll to "Receipt Scanner" section
2. Click "Choose Image File"
3. Upload a clear photo of your receipt
4. Click "Scan Receipt"
5. Review extracted data
6. Click "Use This Data" to pre-fill the form
7. Submit the transaction

#### Import from Bank Statement
1. Scroll to "Transactions" section
2. Click "Import PDF"
3. Upload your bank statement PDF
4. Wait for parsing (may take a few seconds)
5. Review the preview of extracted transactions
6. Click "Import All" to confirm

### 3. Using the AI Assistant

1. Scroll to "AI Financial Assistant" section
2. Either:
   - Click a suggestion button (e.g., "How am I doing financially?")
   - Or type your own question (e.g., "Compare my coffee vs restaurant spending")
3. Click "Ask Claude"
4. Review the insights, charts, and recommendations

**Example Questions**:
- "What are my top 5 expenses this month?"
- "Am I spending more than I earn?"
- "Show me my grocery spending trends"
- "How can I reduce my expenses?"

### 4. Filtering and Exporting

#### Filter Transactions
1. Use the filter controls:
   - **From Date** / **To Date**: Set date range
   - **Type**: Filter by Income/Expense/All
2. Click "Clear Filters" to reset

#### Export to PDF
1. Set desired filters (optional)
2. Click "Export PDF"
3. PDF will be generated and downloaded automatically

### 5. Viewing Statistics

The dashboard automatically displays:
- **Total Income**: Sum of all income transactions
- **Total Expense**: Sum of all expense transactions
- **Balance**: Net amount (Income - Expenses)

These update in real-time based on your active filters.

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'app'`
- **Solution**: Ensure you're in the `backend` directory and virtual environment is activated

**Problem**: Tesseract not found
- **Solution**: Install Tesseract OCR and ensure it's in your PATH, or set `TESSERACT_CMD` in `.env`

**Problem**: Gemini AI errors
- **Solution**: Verify your `GOOGLE_API_KEY` is valid and has access to the Gemini API

### Frontend Issues

**Problem**: `CORS policy` errors
- **Solution**: Ensure backend is running and CORS is configured to allow `http://localhost:3000`

**Problem**: Cannot connect to backend
- **Solution**: Verify backend is running on port 8000 and check `REACT_APP_API_URL`

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- **FastAPI**: For the excellent async web framework
- **Google Gemini**: For powerful AI capabilities
- **Tesseract OCR**: For open-source OCR
- **Chart.js**: For beautiful data visualizations
- **React**: For the component-based UI library

---

## Contact & Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Email: support@typeface-app.com (if applicable)

---

**Happy Tracking! 💰**
