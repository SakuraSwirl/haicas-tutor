"""SQLite persistence for HAICAS Tutor."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DB_PATH = Path(__file__).resolve().parent.parent / "haicas_tutor.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: str | Path = DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                progress TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS questionnaire (
                response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                fear_barrier TEXT NOT NULL,
                skill_level TEXT NOT NULL,
                trust_perception TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                artifact_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
            CREATE TABLE IF NOT EXISTS quiz_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lesson TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, lesson),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
            CREATE TABLE IF NOT EXISTS badges (
                badge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                earned_at TEXT NOT NULL,
                UNIQUE(user_id, name),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
            CREATE TABLE IF NOT EXISTS certificates (
                certificate_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                level TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                artifact_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(artifact_id) REFERENCES artifacts(artifact_id)
            );
            """
        )


def create_user(name: str, email: str = "", db_path: str | Path = DB_PATH) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO users(name, email, created_at) VALUES (?, ?, ?)",
            (name.strip(), email.strip(), utc_now()),
        )
        return int(cursor.lastrowid)


def get_user(user_id: int, db_path: str | Path = DB_PATH) -> sqlite3.Row | None:
    with get_connection(db_path) as connection:
        return connection.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()


def save_questionnaire(user_id: int, fear_barrier: str, skill_level: str, trust_perception: str, db_path: str | Path = DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            "INSERT INTO questionnaire(user_id, fear_barrier, skill_level, trust_perception, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, fear_barrier, skill_level, trust_perception, utc_now()),
        )


def save_artifact(user_id: int, artifact_type: str, content: str, metadata: dict[str, Any] | None = None, db_path: str | Path = DB_PATH) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO artifacts(user_id, artifact_type, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, artifact_type, content.strip(), json.dumps(metadata or {}), utc_now()),
        )
        return int(cursor.lastrowid)


def get_artifacts(user_id: int, db_path: str | Path = DB_PATH) -> list[sqlite3.Row]:
    with get_connection(db_path) as connection:
        return list(connection.execute("SELECT * FROM artifacts WHERE user_id = ? ORDER BY created_at DESC", (user_id,)))


def save_quiz_result(user_id: int, lesson: str, score: int, total: int, passed: bool, db_path: str | Path = DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """INSERT INTO quiz_results(user_id, lesson, score, total, passed, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, lesson) DO UPDATE SET score=excluded.score, total=excluded.total,
            passed=excluded.passed, created_at=excluded.created_at""",
            (user_id, lesson, score, total, int(passed), utc_now()),
        )


def get_passed_lessons(user_id: int, db_path: str | Path = DB_PATH) -> set[str]:
    with get_connection(db_path) as connection:
        rows = connection.execute("SELECT lesson FROM quiz_results WHERE user_id = ? AND passed = 1", (user_id,))
        return {row["lesson"] for row in rows}


def save_badge(user_id: int, name: str, description: str, db_path: str | Path = DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            "INSERT OR IGNORE INTO badges(user_id, name, description, earned_at) VALUES (?, ?, ?, ?)",
            (user_id, name, description, utc_now()),
        )


def get_badges(user_id: int, db_path: str | Path = DB_PATH) -> list[sqlite3.Row]:
    with get_connection(db_path) as connection:
        return list(connection.execute("SELECT * FROM badges WHERE user_id = ? ORDER BY earned_at", (user_id,)))


def save_certificate(certificate_id: str, user_id: int, level: str, artifact_id: int | None, db_path: str | Path = DB_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            "INSERT INTO certificates(certificate_id, user_id, level, issued_at, artifact_id) VALUES (?, ?, ?, ?, ?)",
            (certificate_id, user_id, level, utc_now(), artifact_id),
        )


def get_certificate(user_id: int, db_path: str | Path = DB_PATH) -> sqlite3.Row | None:
    with get_connection(db_path) as connection:
        return connection.execute("SELECT * FROM certificates WHERE user_id = ? ORDER BY issued_at DESC LIMIT 1", (user_id,)).fetchone()
