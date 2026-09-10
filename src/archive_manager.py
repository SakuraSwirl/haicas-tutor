"""Artifact archive helpers."""

from __future__ import annotations

from typing import Any

from .database import get_artifacts, save_artifact


def archive_artifact(user_id: int, content: str, trust_notes: str, lineage: str, tags: str) -> int:
    metadata: dict[str, Any] = {"trust_notes": trust_notes, "lineage": lineage, "tags": tags}
    return save_artifact(user_id, "archive_record", content, metadata)


def get_user_archive(user_id: int):
    return get_artifacts(user_id)
