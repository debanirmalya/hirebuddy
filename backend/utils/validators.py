import os
import re
from werkzeug.datastructures import FileStorage
from utils.exceptions import ValidationError


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_file(file: FileStorage, allowed_extensions: set) -> None:
    """
    Validate uploaded file
    
    Args:
        file: FileStorage object
        allowed_extensions: Set of allowed file extensions
        
    Raises:
        ValidationError: If file is invalid
    """
    if not file:
        raise ValidationError('No file provided')
    
    if file.filename == '':
        raise ValidationError('No file selected')
    
    if not allowed_file(file.filename, allowed_extensions):
        raise ValidationError(
            f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}'
        )
    
    # Check file size (max 16MB)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    max_size = 16 * 1024 * 1024  # 16MB
    if file_size > max_size:
        raise ValidationError(f'File size exceeds maximum limit of 16MB')
    
    if file_size == 0:
        raise ValidationError('File is empty')


def validate_document_type(doc_type: str) -> None:
    """
    Validate document type
    
    Args:
        doc_type: Document type string
        
    Raises:
        ValidationError: If document type is invalid
    """
    valid_types = {'pan', 'aadhaar'}
    
    if not doc_type:
        raise ValidationError('Document type not specified')
    
    if doc_type.lower() not in valid_types:
        raise ValidationError(
            f'Invalid document type. Allowed types: {", ".join(valid_types)}'
        )


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Check if it's a valid number (10-15 digits)
    return len(cleaned) >= 10 and len(cleaned) <= 15 and cleaned.isdigit()


def validate_candidate_data(data: dict) -> None:
    """
    Validate candidate data
    
    Args:
        data: Candidate data dictionary
        
    Raises:
        ValidationError: If data is invalid
    """
    required_fields = ['name', 'email']
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f'Missing required field: {field}')
    
    # Validate email format
    if not validate_email(data.get('email')):
        raise ValidationError('Invalid email format')
    
    # Validate phone if provided
    if data.get('phone') and not validate_phone(data['phone']):
        raise ValidationError('Invalid phone number format')