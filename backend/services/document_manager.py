import os
import shutil
import logging
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)


class DocumentManager:
    """Manages document storage and retrieval"""
    
    def __init__(self, base_upload_folder: str):
        self.base_upload_folder = base_upload_folder
        self.resumes_folder = os.path.join(base_upload_folder, 'resumes')
        self.documents_folder = os.path.join(base_upload_folder, 'documents')
        
        # Create folders if they don't exist
        os.makedirs(self.resumes_folder, exist_ok=True)
        os.makedirs(self.documents_folder, exist_ok=True)
        os.makedirs(os.path.join(self.documents_folder, 'pan'), exist_ok=True)
        os.makedirs(os.path.join(self.documents_folder, 'aadhaar'), exist_ok=True)
    
    def save_resume(self, file: FileStorage, filename: str) -> str:
        """
        Save resume file
        
        Args:
            file: FileStorage object
            filename: Secure filename
            
        Returns:
            Full path to saved file
        """
        try:
            filepath = os.path.join(self.resumes_folder, filename)
            file.save(filepath)
            logger.info(f"Resume saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving resume: {str(e)}")
            raise
    
    def save_document(self, file: FileStorage, filename: str, doc_type: str) -> str:
        """
        Save identity document (PAN/Aadhaar)
        
        Args:
            file: FileStorage object
            filename: Secure filename
            doc_type: Type of document ('pan' or 'aadhaar')
            
        Returns:
            Full path to saved file
        """
        try:
            doc_folder = os.path.join(self.documents_folder, doc_type)
            filepath = os.path.join(doc_folder, filename)
            file.save(filepath)
            logger.info(f"Document saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise
    
    def get_file_path(self, filename: str, doc_type: str = None) -> str:
        """
        Get full path to a file
        
        Args:
            filename: Name of the file
            doc_type: Type of document (None for resumes, 'pan'/'aadhaar' for documents)
            
        Returns:
            Full file path
        """
        if doc_type:
            return os.path.join(self.documents_folder, doc_type, filename)
        else:
            return os.path.join(self.resumes_folder, filename)
    
    def file_exists(self, filename: str, doc_type: str = None) -> bool:
        """Check if a file exists"""
        filepath = self.get_file_path(filename, doc_type)
        return os.path.exists(filepath)
    
    def delete_file(self, filename: str, doc_type: str = None) -> bool:
        """
        Delete a file
        
        Args:
            filename: Name of the file
            doc_type: Type of document
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            filepath = self.get_file_path(filename, doc_type)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"File deleted: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def get_file_size(self, filename: str, doc_type: str = None) -> int:
        """Get file size in bytes"""
        filepath = self.get_file_path(filename, doc_type)
        if os.path.exists(filepath):
            return os.path.getsize(filepath)
        return 0
    
    def cleanup_candidate_files(self, candidate_id: str) -> None:
        """
        Delete all files associated with a candidate
        
        Args:
            candidate_id: Candidate ID
        """
        try:
            # Find and delete resume
            for filename in os.listdir(self.resumes_folder):
                if filename.startswith(candidate_id):
                    filepath = os.path.join(self.resumes_folder, filename)
                    os.remove(filepath)
                    logger.info(f"Deleted resume: {filepath}")
            
            # Find and delete documents
            for doc_type in ['pan', 'aadhaar']:
                doc_folder = os.path.join(self.documents_folder, doc_type)
                for filename in os.listdir(doc_folder):
                    if filename.startswith(candidate_id):
                        filepath = os.path.join(doc_folder, filename)
                        os.remove(filepath)
                        logger.info(f"Deleted document: {filepath}")
        
        except Exception as e:
            logger.error(f"Error cleaning up files for candidate {candidate_id}: {str(e)}")
            raise