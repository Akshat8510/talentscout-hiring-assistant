import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

DATA_PATH = Path(os.getenv("DATA_STORAGE_PATH", "./data/candidates.json"))

def _ensure_storage():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        DATA_PATH.write_text(json.dumps([]))

def save_candidate(candidate_data: dict) -> bool:
    try:
        _ensure_storage()
        records = json.loads(DATA_PATH.read_text())
        email = candidate_data.get("Email Address", "")
        record = {
            "session_id": candidate_data.get("session_id", "unknown"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "full_name": candidate_data.get("Full Name", ""),
            "email_hash": hashlib.sha256(email.encode()).hexdigest()[:16] + "***",
            "location": candidate_data.get("Current Location", ""),
            "experience_years": candidate_data.get("Years of Experience", ""),
            "desired_positions": candidate_data.get("Desired Position(s)", ""),
            "tech_stack": candidate_data.get("Tech Stack", ""),
            "contact": {"email": email, "phone": candidate_data.get("Phone Number", "")},
        }
        records.append(record)
        DATA_PATH.write_text(json.dumps(records, indent=2))
        return True
    except Exception as e:
        print(f"[DataHandler] Failed to save: {e}")
        return False