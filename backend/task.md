The Challenge
Build a full-stack system that parses resumes, extracts candidate information, and uses an AI
agent to autonomously collect PAN and Aadhaar documents.
Context: An HR team uploads a candidate's resume. Your system extracts their details, then an
AI agent intelligently requests identity documents via their email or phone.
What to Build
Backend
● POST /candidates/upload - Accept resume (PDF/DOCX)
● GET /candidates - List all candidates
● GET /candidates/<id> - Show parsed profile with extracted data (name, email,
phone, company, designation, skills)
● POST /candidates/<id>/request-documents - AI agent generates and logs a
personalized request for PAN/Aadhaar
● POST /candidates/<id>/submit-documents - Accept uploaded PAN/Aadhaar
images
Stack
● Python (Django), React, OpenAI API (GPT-4) or Claude or OpenRouter (whatever
is free and available to you)
● LangChain or similar for agent orchestration
● SQLite/PostgreSQL, deploy to Render/Railway/Vercel