"""SQLite persistence for tool run history (stdlib sqlite3, WAL mode)."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any

from .core.config import DB_PATH, ensure_data_dir

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool TEXT NOT NULL,
    title TEXT NOT NULL,
    score REAL,
    input_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    ai_analysis TEXT,
    created_at TEXT NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(_SCHEMA)


def insert_run(
    tool: str,
    title: str,
    score: float | None,
    input_data: dict[str, Any],
    result_data: dict[str, Any],
) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO runs (tool, title, score, input_json, result_json, ai_analysis, created_at)"
            " VALUES (?, ?, ?, ?, ?, NULL, ?)",
            (tool, title, score, json.dumps(input_data, ensure_ascii=False),
             json.dumps(result_data, ensure_ascii=False), created_at),
        )
        return int(cur.lastrowid)


def list_runs(tool: str | None = None) -> list[dict[str, Any]]:
    with _connect() as conn:
        if tool:
            rows = conn.execute(
                "SELECT id, tool, title, score, created_at FROM runs WHERE tool = ?"
                " ORDER BY created_at DESC",
                (tool,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, tool, title, score, created_at FROM runs ORDER BY created_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]


def get_run(run_id: int) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        return None
    data = dict(row)
    data["input"] = json.loads(data.pop("input_json"))
    data["result"] = json.loads(data.pop("result_json"))
    return data


def delete_run(run_id: int) -> bool:
    with _connect() as conn:
        cur = conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
        return cur.rowcount > 0


def update_analysis(run_id: int, analysis: str) -> bool:
    with _connect() as conn:
        cur = conn.execute(
            "UPDATE runs SET ai_analysis = ? WHERE id = ?", (analysis, run_id)
        )
        return cur.rowcount > 0
