import os
import json
import math
import sqlite3
from typing import Dict, Any, Optional


class CandidateStore:
    """SQLite-backed store for candidate records."""

    def __init__(self, data_folder: str):
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)
        self.db_path = os.path.join(self.data_folder, 'traqcheck.db')
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self) -> None:
        """Create table if not exists and ensure new columns exist."""
        with self._get_connection() as conn:
            # Initial table creation (with new columns)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS candidates (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    curr_company TEXT,
                    resume_filename TEXT,
                    resume_path TEXT,
                    parsed_data TEXT,
                    documents TEXT,
                    document_requests TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )

            # Ensure new columns exist (for backward compatibility)
            existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(candidates)").fetchall()}
            for col in ["name", "email", "curr_company"]:
                if col not in existing_cols:
                    conn.execute(f"ALTER TABLE candidates ADD COLUMN {col} TEXT;")
            conn.commit()

    def save_candidate(self, candidate: Dict[str, Any]) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO candidates (
                    id, name, email, curr_company, resume_filename, resume_path,
                    parsed_data, documents, document_requests, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.get('id'),
                    candidate.get('name'),
                    candidate.get('email'),
                    candidate.get('curr_company'),
                    candidate.get('resume_filename'),
                    candidate.get('resume_path'),
                    json.dumps(candidate.get('parsed_data') or {}),
                    json.dumps(candidate.get('documents') or {}),
                    json.dumps(candidate.get('document_requests') or []),
                    candidate.get('status'),
                    candidate.get('created_at'),
                    candidate.get('updated_at'),
                ),
            )
            conn.commit()

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM candidates WHERE id = ?",
                (candidate_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_dict(row)

    def update_candidate(self, candidate_id: str, candidate: Dict[str, Any]) -> None:
        existing = self.get_candidate(candidate_id)
        if not existing:
            raise ValueError(f"Candidate {candidate_id} not found")

        merged = {**existing, **candidate}  # new data overrides old

        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE candidates
                SET name = ?, email = ?, curr_company = ?, resume_filename = ?, resume_path = ?,
                    parsed_data = ?, documents = ?, document_requests = ?, status = ?,
                    created_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    merged.get('name'),
                    merged.get('email'),
                    merged.get('curr_company'),
                    merged.get('resume_filename'),
                    merged.get('resume_path'),
                    json.dumps(merged.get('parsed_data') or {}),
                    json.dumps(merged.get('documents') or {}),
                    json.dumps(merged.get('document_requests') or []),
                    merged.get('status'),
                    merged.get('created_at'),
                    merged.get('updated_at'),
                    candidate_id,
                ),
            )
            conn.commit()

    def list_candidates(self, page: int, per_page: int, status: Optional[str] = None) -> Dict[str, Any]:
        offset = (page - 1) * per_page
        params = []
        where_clause = ""
        if status:
            where_clause = "WHERE status = ?"
            params.append(status)

        with self._get_connection() as conn:
            # total count
            cur = conn.execute(f"SELECT COUNT(1) as cnt FROM candidates {where_clause}", params)
            total = int(cur.fetchone()[0])

            # items
            cur = conn.execute(
                f"""
                SELECT id, name, email, curr_company, resume_filename, resume_path,
                       parsed_data, documents, document_requests, status, created_at, updated_at
                FROM candidates
                {where_clause}
                ORDER BY datetime(created_at) DESC
                LIMIT ? OFFSET ?
                """,
                (*params, per_page, offset),
            )
            items = [self._row_to_dict(r) for r in cur.fetchall()]

        pages = max(1, math.ceil(total / per_page)) if per_page else 1
        return {
            'items': items,
            'total': total,
            'pages': pages,
        }

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'curr_company': row['curr_company'],
            'resume_filename': row['resume_filename'],
            'resume_path': row['resume_path'],
            'parsed_data': self._safe_json_load(row['parsed_data'], {}),
            'documents': self._safe_json_load(row['documents'], {}),
            'document_requests': self._safe_json_load(row['document_requests'], []),
            'status': row['status'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
        }

    def _safe_json_load(self, value: Optional[str], default: Any) -> Any:
        try:
            return json.loads(value) if value else default
        except Exception:
            return default
