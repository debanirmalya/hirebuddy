from flask import Blueprint, current_app, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from tasks.generate_doc_request import generate_doc_request_background
from tasks.parse_resume_llm import process_resume_background
from utils.exceptions import ValidationError, ProcessingError, NotFoundError
from celery.exceptions import TimeoutError, OperationalError
from utils.validators import validate_file, validate_document_type
import os

bp = Blueprint("candidates", __name__)

# Dependency injection globals
g_resume_parser = g_ai_agent = g_document_manager = g_candidate_store = None


def register_routes(app, *, resume_parser, ai_agent, document_manager, candidate_store):
    global g_resume_parser, g_ai_agent, g_document_manager, g_candidate_store
    g_resume_parser = resume_parser
    g_ai_agent = ai_agent
    g_document_manager = document_manager
    g_candidate_store = candidate_store
    app.register_blueprint(bp)


@bp.route("/uploads/<path:filename>")
def serve_upload(filename):
    uploads_dir = os.path.join(current_app.root_path, "uploads")
    return send_from_directory(uploads_dir, filename)


@bp.route("/candidates/upload", methods=["POST"])
def upload_resume():
    """
    Upload a resume and create a new candidate.
    Requires: file, name, email, curr_company
    """
    if "file" not in request.files:
        raise ValidationError("No file provided")

    name = request.form.get("name")
    email = request.form.get("email")
    curr_company = request.form.get("curr_company")
    if not all([name, email, curr_company]):
        raise ValidationError(
            "Missing required fields: name, email, curr_company are mandatory"
        )

    file = request.files["file"]
    if file.filename == "":
        raise ValidationError("No file selected")

    validate_file(file, {"pdf", "docx", "doc"})

    candidate_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{candidate_id}_{timestamp}_{filename}"
    resume_path = g_document_manager.save_resume(file, unique_filename)

    candidate = {
        "id": candidate_id,
        "name": name,
        "email": email,
        "curr_company": curr_company,
        "resume_filename": unique_filename,
        "resume_path": resume_path,
        "parsed_data": None,
        "documents": {"pan": None, "aadhaar": None},
        "document_requests": [],
        "status": "parsing_resume",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    g_candidate_store.save_candidate(candidate)

    # Trigger Celery background task
    process_resume_background.delay(candidate_id, resume_path)

    return (
        jsonify(
            {
                "message": "Resume uploaded successfully, parsing in background",
                "candidate_id": candidate_id,
                "status": "parsing_resume",
            }
        ),
        202,
    )


@bp.route("/candidates", methods=["GET"])
def list_candidates():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    status = request.args.get("status", None)
    if per_page > 100:
        per_page = 100

    try:
        candidates = g_candidate_store.list_candidates(page, per_page, status)
        return (
            jsonify(
                {
                    "candidates": candidates["items"],
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": candidates["total"],
                        "pages": candidates["pages"],
                    },
                }
            ),
            200,
        )
    except Exception:
        raise ProcessingError("Failed to retrieve candidates")


@bp.route("/candidates/<candidate_id>", methods=["GET"])
def get_candidate(candidate_id):
    try:
        candidate = g_candidate_store.get_candidate(candidate_id)
        if not candidate:
            raise NotFoundError(f"Candidate {candidate_id} not found")
        return jsonify({"candidate": candidate}), 200
    except NotFoundError:
        raise
    except Exception:
        raise ProcessingError("Failed to retrieve candidate details")


@bp.route("/candidates/<candidate_id>/request-documents", methods=["POST"])
def request_documents(candidate_id):
    try:
        candidate = g_candidate_store.get_candidate(candidate_id)
        if not candidate:
            raise NotFoundError(f"Candidate {candidate_id} not found")

        g_candidate_store.update_candidate(
            candidate_id,
            {
                "status": "document_request_pending",
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        try:
            task = generate_doc_request_background.apply_async(
                (candidate_id,), retry=False
            )
            print(task)
            # Optionally check broker acknowledgment
            if not task:
                raise ProcessingError("Failed to queue task — broker unavailable")

        except (OperationalError, ConnectionError) as e:
            current_app.logger.error(f"Celery broker connection failed: {e}")
            raise ProcessingError(
                "Document request could not be queued — Celery broker is down"
            )

        except Exception as e:
            current_app.logger.error(f"Celery enqueue error: {e}")
            raise ProcessingError(
                "Candidate updated but failed to queue document request task"
            )

        return (
            jsonify(
                {
                    "message": "Document request task started",
                    "candidate_id": candidate_id,
                    "status": "document_request_pending",
                }
            ),
            202,
        )

    except NotFoundError:
        raise
    except ProcessingError:
        raise
    except Exception as e:
        current_app.logger.error(f"Unhandled error: {e}")
        raise ProcessingError(f"Failed to queue document request task: {e}")


@bp.route("/candidates/<candidate_id>/submit-documents", methods=["POST"])
def submit_documents(candidate_id):
    try:
        candidate = g_candidate_store.get_candidate(candidate_id)
        if not candidate:
            raise NotFoundError(f"Candidate {candidate_id} not found")

        if "files" not in request.files:
            raise ValidationError("No files provided")

        files = request.files.getlist("files")
        document_types = request.form.getlist("types")
        if len(files) != len(document_types):
            raise ValidationError("Number of files must match number of document types")

        uploaded_docs = []
        for file, doc_type in zip(files, document_types):
            validate_document_type(doc_type)
            validate_file(file, {"pdf", "jpg", "jpeg", "png"})

            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{candidate_id}_{doc_type}_{timestamp}_{filename}"
            doc_path = g_document_manager.save_document(file, unique_filename, doc_type)

            candidate["documents"][doc_type] = {
                "filename": unique_filename,
                "path": doc_path,
                "uploaded_at": datetime.utcnow().isoformat(),
            }

            uploaded_docs.append({"type": doc_type, "filename": unique_filename})

        if candidate["documents"]["pan"] and candidate["documents"]["aadhaar"]:
            candidate["status"] = "completed"
        else:
            candidate["status"] = "partially_completed"

        candidate["updated_at"] = datetime.utcnow().isoformat()
        g_candidate_store.update_candidate(candidate_id, candidate)

        return (
            jsonify(
                {
                    "message": "Documents uploaded successfully",
                    "uploaded": uploaded_docs,
                    "status": candidate["status"],
                }
            ),
            200,
        )

    except (NotFoundError, ValidationError):
        raise
    except Exception:
        raise ProcessingError("Failed to upload documents")
