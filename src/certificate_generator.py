"""Certificate eligibility and IDs."""

from __future__ import annotations

import uuid
from pathlib import Path

from .database import DB_PATH, get_artifacts, get_certificate, save_certificate


def generate_certificate_id() -> str:
    return f"HAICAS-{uuid.uuid4().hex[:12].upper()}"


def issue_certificate(user_id: int, completed_lessons: set[str], db_path: str | Path = DB_PATH) -> str | None:
    required = {"Vision Anchor", "Challenge", "Scaffolding", "Artifact", "Archive"}
    if not required.issubset(completed_lessons):
        return None
    existing = get_certificate(user_id, db_path=db_path)
    if existing:
        return str(existing["certificate_id"])
    artifacts = get_artifacts(user_id, db_path=db_path)
    artifact_id = artifacts[0]["artifact_id"] if artifacts else None
    certificate_id = generate_certificate_id()
    save_certificate(certificate_id, user_id, "Literacy", artifact_id, db_path=db_path)
    return certificate_id
