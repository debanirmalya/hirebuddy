
# 🤖 HireBuddy — AI-Powered Candidate Verification System

HireBuddy is a **modern full-stack AI application** that streamlines the **candidate verification process** for HR teams.  
It automatically parses resumes, extracts candidate details, and uses an **AI agent** to request and manage **PAN & Aadhaar document verification**.

---

## 🧭 System Overview

HireBuddy connects a **Next.js frontend**, a **Flask backend**, and a **local AI engine (Ollama)** to create a fully automated candidate verification pipeline.

### 🏗️ Architecture Diagram
```mermaid
flowchart TD
    A["👤 HR Uploads Resume (PDF/DOCX)"] --> B["📤 Backend API Receives File"]
    B --> C["🧠 AI Resume Parser (Ollama LLM)"]
    C --> D["🗃️ Extract Candidate Data (Name, Email, Phone, Skills)"]
    D --> E[("💾 Save to SQLite Database")]
    E --> F["🌐 Frontend Dashboard Displays Candidate Info"]

    F --> G["🤖 HR Triggers 'Request Documents'"]
    G --> H["🧠 AI Agent Generates Personalized PAN/Aadhaar Request"]
    H --> I["📩 Sends Message (Email/SMS Mock)"]
    I --> J["🕒 Wait for Candidate Response"]
    J --> K["📎 Candidate Uploads PAN/Aadhaar"]
    K --> L["🗂️ Store Documents + Update Verification Status"]
    L --> M["✅ HR Reviews and Confirms Verification"]
````

---

## ✨ Features

### 📄 AI-Powered Resume Parsing

* Automatically extracts candidate details (name, email, phone, company, designation, skills)
* Supports PDF and DOCX resume formats
* Confidence scoring for each extracted attribute

### 🤖 Intelligent Document Requests

* AI Agent drafts personalized PAN/Aadhaar document request messages
* Logs requests for audit and review
* Seamless upload and verification workflow

### 📊 Interactive Candidate Dashboard

* Real-time list of uploaded candidates
* Extraction status and confidence indicators
* View and upload PAN/Aadhaar directly from the profile page

### ⚙️ Tech Highlights

* **Frontend:** Next.js 14, React, Tailwind CSS
* **Backend:** Flask (Python)
* **AI Layer:** Ollama LLM (local large language model)
* **Queue:** Celery + Redis for async processing
* **Database:** SQLite (can easily upgrade to PostgreSQL)
* **Deployment:** Vercel (frontend) + Render/Railway (backend)

---

## 📁 Project Structure

```
hirebuddy/
├── backend/                 
│   ├── app.py               # Flask application entrypoint
│   ├── celery_worker.py     # Background task processor
│   ├── models/              # ORM models
│   ├── routes/              # REST API routes
│   ├── services/            # Core business logic
│   ├── tasks/               # Celery async jobs
│   └── utils/               # Helper functions
│
└── frontend/               
    ├── app/                 # Next.js app router pages
    ├── components/          # Reusable React components
    ├── lib/                 # API client and configuration
    └── utils/               # Common utilities
```

---

## 🧩 Prerequisites

### Backend

* Python 3.8+
* [Ollama](https://ollama.ai) installed locally for LLM inference
* Redis (for Celery background tasks)

### Frontend

* Node.js 16+
* npm or yarn

---

## ⚙️ Installation Guide

### 1️⃣ Clone Repository

```bash
git clone https://github.com/<your-username>/hirebuddy.git
cd hirebuddy
```

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Create `.env` file in `/backend`

```bash
FLASK_ENV=development
OLLAMA_MODEL=llama3:instruct
OLLAMA_BASE_URL=http://localhost:11434
```

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
```

#### Create `.env.local` in `/frontend`

```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## 🚀 Running the Application

### Start Backend

```bash
cd backend
python app.py
# (Optional) Start Celery worker
celery -A celery_worker worker --loglevel=info
```

### Start Frontend

```bash
cd frontend
npm run dev
```

* Frontend → [http://localhost:3000](http://localhost:3000)
* Backend → [http://localhost:5000](http://localhost:5000)

---

## 🔗 API Reference

| Method | Endpoint                                 | Description                              |
| ------ | ---------------------------------------- | ---------------------------------------- |
| `POST` | `/api/candidates/upload`                 | Upload and parse a resume                |
| `GET`  | `/api/candidates`                        | List all candidates                      |
| `GET`  | `/api/candidates/{id}`                   | Retrieve candidate details               |
| `POST` | `/api/candidates/{id}/request-documents` | Trigger AI-generated PAN/Aadhaar request |
| `POST` | `/api/candidates/{id}/documents`         | Upload verification documents            |
| `GET`  | `/api/health`                            | Health check endpoint                    |

---

## 🧠 Example AI Output

### Parsed Resume Data

```json
{
  "name": "Arpan Sharma",
  "email": "arpan@example.com",
  "phone": "+91-9876543210",
  "skills": ["Python", "React", "AWS"],
  "company": "TechCorp",
  "designation": "Full Stack Engineer",
  "confidence": {
    "name": 0.97,
    "email": 0.92,
    "skills": 0.88
  }
}
```

### AI-Generated Document Request

```json
{
  "candidate_id": "abc123",
  "message": "Dear Arpan, as part of our HR record process, please share your PAN and Aadhaar cards with hr@hirebuddy.com for verification.",
  "timestamp": "2025-11-01T10:30:00Z",
  "status": "sent"
}
```

---

## 🧩 Future Enhancements

* 🔐 Integrate Gmail/Twilio API for real message delivery
* 📈 Add confidence visualization charts
* 🪄 Enhance parsing via RAG (Resume + JD context)
* ☁️ Cloud deployment (AWS/GCP/Railway + Vercel)
* 🧩 Switch SQLite → PostgreSQL for production

---

## 🎥 Demo (Loom)

👉 **[Watch Demo Video](https://www.loom.com/share/587dfd913c7e4e899e6b872c5d7fa113)**
*(A 3–5 minute Loom walkthrough: architecture → resume upload → parsed data → AI document request → document upload)*

---
