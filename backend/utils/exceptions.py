
class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class ProcessingError(Exception):
    """Raised when processing fails"""
    pass


class NotFoundError(Exception):
    """Raised when resource is not found"""
    pass


class StorageError(Exception):
    """Raised when storage operation fails"""
    pass


class AIServiceError(Exception):
    """Raised when AI service call fails"""
    pass