from flask import Flask
from flask_cors import CORS
import os
from datetime import datetime
import uuid
import logging
from logging.handlers import RotatingFileHandler
from config import Config
from services.resume_parser import ResumeParser
from services.ai_agent import AIAgent
from services.document_manager import DocumentManager
from models.candidate import CandidateStore
from utils.validators import validate_file, validate_document_type
from utils.exceptions import ValidationError, ProcessingError, NotFoundError
from routes import candidates, health

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Resume Parser API startup')

# Initialize services
resume_parser = ResumeParser(app.config['OLLAMA_MODEL'])
ai_agent = AIAgent(app.config['OLLAMA_MODEL'])
document_manager = DocumentManager(app.config['RESUME_FOLDER'])
candidate_store = CandidateStore(app.config['DATA_FOLDER'])

# --- REGISTER ROUTES ---
candidates.register_routes(
    app,
    resume_parser=resume_parser,
    ai_agent=ai_agent,
    document_manager=document_manager,
    candidate_store=candidate_store
)
health.register_routes(app)

# Error handlers still in app.py
@app.errorhandler(ValidationError)
def handle_validation_error(e):
    return {"error": str(e), "type": "validation_error"}, 400
@app.errorhandler(ProcessingError)
def handle_processing_error(e):
    return {"error": str(e), "type": "processing_error"}, 500
@app.errorhandler(NotFoundError)
def handle_not_found_error(e):
    return {"error": str(e), "type": "not_found"}, 404
@app.errorhandler(Exception)
def handle_generic_error(e):
    app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
    return {"error": "Internal server error", "type": "server_error"}, 500

if __name__ == '__main__':
    os.makedirs(app.config['RESUME_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOCUMENTS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
