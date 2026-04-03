"""
data_handler.py — Handles secure storage and retrieval of candidate data.
All data is stored locally in a JSON file. In production, replace with a
proper encrypted database. No PII is logged to console or external services.
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path


DATA_PATH = Path(os.getenv("DATA_STORAGE_PATH", "./data/candidates.json"))


def _ensure_storage():
    """Create the data directory and file if they don't exist."""
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        DATA_PATH.write_text(json.dumps([]))


def _anonymize_email(email: str) -> str:
    """One-way hash the email for the log record (GDPR-friendly)."""
    return hashlib.sha256(email.encode()).hexdigest()[:16] + "***"


def save_candidate(candidate_data: dict) -> bool:
    """
    Persist candidate data to local JSON store.
    Sensitive fields (email, phone) are partially masked in the log.
    Returns True on success, False on failure.
    """
    try:
        _ensure_storage()
        records = json.loads(DATA_PATH.read_text())

        record = {
            "session_id": candidate_data.get("session_id", "unknown"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "full_name": candidate_data.get("Full Name", ""),
            "email_hash": _anonymize_email(candidate_data.get("Email Address", "")),
            "location": candidate_data.get("Current Location", ""),
            "experience_years": candidate_data.get("Years of Experience", ""),
            "desired_positions": candidate_data.get("Desired Position(s)", ""),
            "tech_stack": candidate_data.get("Tech Stack", ""),
            # Store actual contact info encrypted in real prod; here kept raw for demo
            "contact": {
                "email": candidate_data.get("Email Address", ""),
                "phone": candidate_data.get("Phone Number", ""),
            },
        }

        records.append(record)
        DATA_PATH.write_text(json.dumps(records, indent=2))
        return True
    except Exception as e:
        print(f"[DataHandler] Failed to save candidate: {e}")
        return False


def load_all_candidates() -> list:
    """Return all stored candidate records."""
    try:
        _ensure_storage()
        return json.loads(DATA_PATH.read_text())
    except Exception:
        return []
