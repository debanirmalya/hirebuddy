# Resume Parser & Document Collection API

A production-grade Flask backend that parses resumes, extracts candidate information, and uses an AI agent to autonomously collect PAN and Aadhaar documents.

## Features

- 📄 **Resume Parsing**: Extracts structured data from PDF/DOCX resumes using Ollama LLM
- 🤖 **AI Agent**: Generates personalized document requests
- 📁 **Local Storage**: Securely stores documents locally
- 🔒 **Validation**: Comprehensive input validation and error handling
- 📊 **RESTful API**: Clean API design with proper HTTP methods
- 🪵 **Logging**: Rotating file logs for debugging and monitoring
- 🧵 **Thread-Safe**: Thread-safe data storage

## Architecture

```
resume-parser-api/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── services/
│   ├── __init__.py
│   ├── resume_parser.py  # Resume parsing with LLM
│   ├── ai_agent.py       # AI-powered document requests
│   └── document_manager.py # File storage management
├── models/
│   ├── __init__.py
│   └── candidate.py      # Candidate data store
├── utils/
│   ├── __init__.py
│   ├── validators.py     # Input validation
│   └── exceptions.py     # Custom exceptions
├── uploads/              # File storage (gitignored)
│   ├── resumes/
│   └── documents/
│       ├── pan/
│       └── aadhaar/
├── data/                 # JSON data store (gitignored)
└── logs/                 # Application logs (gitignored)
```

## Prerequisites

- Python 3.8+
- Ollama installed and running locally
- At least one Ollama model downloaded (e.g., llama3.2)

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd resume-parser-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup Ollama**
```bash
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull llama3.2
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

6. **Create required directories**
```bash
mkdir -p uploads/resumes uploads/documents/pan uploads/documents/aadhaar data logs
```

## Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T10:00:00",
  "service": "resume-parser-api"
}
```

### 2. Upload Resume
```http
POST /candidates/upload
Content-Type: multipart/form-data

file: <resume.pdf|resume.docx>
```

**Response:**
```json
{
  "message": "Resume uploaded and parsed successfully",
  "candidate_id": "uuid-here",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+91-9876543210",
    "current_company": "Tech Corp",
    "designation": "Senior Engineer",
    "skills": ["Python", "AWS", "Docker"],
    "experience_years": 5,
    "education": "B.Tech Computer Science",
    "location": "Mumbai"
  }
}
```

### 3. List Candidates
```http
GET /candidates?page=1&per_page=10&status=pending_documents
```

**Response:**
```json
{
  "candidates": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 50,
    "pages": 5
  }
}
```

### 4. Get Candidate Details
```http
GET /candidates/<candidate_id>
```

**Response:**
```json
{
  "candidate": {
    "id": "uuid-here",
    "parsed_data": {...},
    "documents": {
      "pan": null,
      "aadhaar": null
    },
    "status": "pending_documents",
    "created_at": "2025-10-31T10:00:00"
  }
}
```

### 5. Request Documents (AI Agent)
```http
POST /candidates/<candidate_id>/request-documents
```

**Response:**
```json
{
  "message": "Document request generated successfully",
  "request": "Dear John Doe,\n\nThank you for your interest..."
}
```

### 6. Submit Documents
```http
POST /candidates/<candidate_id>/submit-documents
Content-Type: multipart/form-data

files: <file1>, <file2>
types: pan, aadhaar
```

**Response:**
```json
{
  "message": "Documents uploaded successfully",
  "uploaded": [
    {"type": "pan", "filename": "..."},
    {"type": "aadhaar", "filename": "..."}
  ],
  "status": "completed"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | development |
| `FLASK_DEBUG` | Enable debug mode | True |
| `SECRET_KEY` | Flask secret key | (required in production) |
| `OLLAMA_BASE_URL` | Ollama API URL | http://localhost:11434 |
| `OLLAMA_MODEL` | Model to use | llama3.2 |
| `CORS_ORIGINS` | Allowed CORS origins | * |

## Data Storage

### File Structure
```
uploads/
├── resumes/
│   └── <candidate_id>_<timestamp>_<filename>
└── documents/
    ├── pan/
    │   └── <candidate_id>_pan_<timestamp>_<filename>
    └── aadhaar/
        └── <candidate_id>_aadhaar_<timestamp>_<filename>

data/
└── candidates.json  # JSON database
```

### Candidate Status Flow
1. `pending_documents` - Resume uploaded, waiting for documents
2. `partially_completed` - Some documents submitted
3. `completed` - All documents submitted

## Error Handling

The API uses structured error responses:

```json
{
  "error": "Error message",
  "type": "validation_error|processing_error|not_found|server_error"
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Validation Error
- `404` - Not Found
- `500` - Server Error

## Logging

Logs are stored in `logs/app.log` with automatic rotation:
- Maximum size: 10MB per file
- Backup count: 10 files
- Format: `timestamp level: message [file:line]`

## Security Features

- ✅ Input validation for all endpoints
- ✅ Secure filename handling
- ✅ File type restrictions
- ✅ File size limits (16MB)
- ✅ Thread-safe data operations
- ✅ CORS configuration
- ✅ Error message sanitization

## Testing with cURL

### Upload Resume
```bash
curl -X POST http://localhost:5000/candidates/upload \
  -F "file=@resume.pdf"
```

### Get Candidates
```bash
curl http://localhost:5000/candidates
```

### Request Documents
```bash
curl -X POST http://localhost:5000/candidates/<id>/request-documents
```

### Submit Documents
```bash
curl -X POST http://localhost:5000/candidates/<id>/submit-documents \
  -F "files=@pan.pdf" \
  -F "files=@aadhaar.pdf" \
  -F "types=pan" \
  -F "types=aadhaar"
```

## Performance Considerations

- **LLM Processing**: Resume parsing takes 5-30 seconds depending on model and hardware
- **File Storage**: Local filesystem storage for simplicity
- **Concurrency**: Thread-safe operations for multiple simultaneous requests
- **Pagination**: Default 10 items per page, max 100

## Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Background job processing (Celery)
- [ ] Document OCR for better extraction
- [ ] Email/SMS integration for notifications
- [ ] Authentication & authorization
- [ ] Rate limiting
- [ ] Document encryption at rest
- [ ] S3/cloud storage integration
- [ ] Webhook support

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/version

# Start Ollama
ollama serve
```

### Permission Errors
```bash
# Ensure directories are writable
chmod -R 755 uploads/ data/ logs/
```

### Import Errors
```bash
# Create __init__.py files
touch services/__init__.py models/__init__.py utils/__init__.py
```

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.