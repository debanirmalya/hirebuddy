import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'png', 'jpg', 'jpeg'}
    
    # Directories
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
    DOCUMENTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'documents')
    DATA_FOLDER = os.path.join(BASE_DIR, 'data')

    
    # Ollama settings
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3:instruct')
    OLLAMA_TIMEOUT = 120  # seconds
    
    # Security
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = True
    # if not os.environ.get('SECRET_KEY'):
    #     raise ValueError("SECRET_KEY environment variable must be set in production")


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
