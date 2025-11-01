import logging
from datetime import datetime
from celery_worker import celery_app
import os, sys

sys.path.append(os.getcwd())


logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.process_resume_background")
def process_resume_background(candidate_id: str, resume_path: str):
    """Celery task to parse resume and update candidate record"""
    from app import resume_parser, candidate_store  

    try:
        logger.info(f"Starting background resume parsing for {candidate_id}")
        parsed_data = resume_parser.parse_resume(resume_path)
        
        candidate_store.update_candidate(candidate_id, {
            "parsed_data": parsed_data,
            "status": "pending_documents",
            "updated_at": datetime.utcnow().isoformat(),
        })
        logger.info(f"✅ Resume parsing completed for candidate {candidate_id}")
    except Exception as e:
        logger.error(f"❌ Failed to parse resume for {candidate_id}: {e}")
        candidate_store.update_candidate(candidate_id, {
            "status": "parse_failed",
            "updated_at": datetime.utcnow().isoformat(),
        })
