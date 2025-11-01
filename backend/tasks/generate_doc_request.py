import logging
from datetime import datetime
from celery_worker import celery_app
import os, sys
import json

sys.path.append(os.getcwd())

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.generate_doc_request_background")
def generate_doc_request_background(candidate_id: str):
    """
    Celery task to asynchronously generate a personalized document request
    message for a candidate using the AI Agent.
    """
    from app import candidate_store, ai_agent  

    try:
        logger.info(f"🚀 Starting document request generation for candidate {candidate_id}")

        # Fetch candidate data
        candidate = candidate_store.get_candidate(candidate_id)
        if not candidate:
            logger.error(f"❌ Candidate not found: {candidate_id}")
            return

        parsed_data = candidate.get("parsed_data", {}).get("parsed_data", {}) or {}
        request_message = ai_agent.generate_document_request(parsed_data)

        # Load existing document requests list (or start fresh)
        existing_requests = candidate.get("document_requests")
        if isinstance(existing_requests, str):
            try:
                existing_requests = json.loads(existing_requests)
            except json.JSONDecodeError:
                existing_requests = []
        elif not existing_requests:
            existing_requests = []

        # Append the new request log
        new_request = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": request_message,
            "status": "sent"
        }
        existing_requests.append(new_request)

        # Update candidate record
        candidate_store.update_candidate(candidate_id, {
            "document_requests": json.dumps(existing_requests),
            "status": "document_requested",
            "updated_at": datetime.utcnow().isoformat(),
        })

        logger.info(f"✅ Document request message generated for candidate {candidate_id}")

    except Exception as e:
        logger.error(f"❌ Failed to generate document request for {candidate_id}: {e}")
        candidate_store.update_candidate(candidate_id, {
            "status": "document_request_failed",
            "updated_at": datetime.utcnow().isoformat(),
        })
