import csv
import io
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


_DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "experiment_records.db"
DB_PATH = Path(os.getenv("QUANTUM_PLATFORM_DB_PATH", str(_DEFAULT_DB_PATH)))


def _ensure_db_dir() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_conn() -> sqlite3.Connection:
    _ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_record_db() -> None:
    conn = _get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS experiment_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_url TEXT NOT NULL,
                page_title TEXT,
                params_json TEXT NOT NULL,
                explanation TEXT,
                note TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
            """
        )
        # Lightweight migration for older DB files.
        cols = conn.execute("PRAGMA table_info(experiment_records)").fetchall()
        col_names = {c[1] for c in cols}
        if "note" not in col_names:
            conn.execute("ALTER TABLE experiment_records ADD COLUMN note TEXT DEFAULT ''")
        conn.commit()
    finally:
        conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    params_json = row["params_json"] or "{}"
    try:
        params = json.loads(params_json)
    except json.JSONDecodeError:
        params = {}

    return {
        "id": int(row["id"]),
        "page_url": row["page_url"] or "",
        "page_title": row["page_title"] or "",
        "params": params,
        "explanation": row["explanation"] or "",
        "note": row["note"] or "",
        "created_at": row["created_at"] or "",
    }


def create_record(
    page_url: str,
    page_title: str = "",
    params: dict[str, Any] | None = None,
    explanation: str = "",
    note: str = "",
) -> dict[str, Any]:
    if not page_url:
        raise ValueError("page_url is required")

    safe_params = params or {}
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    params_json = json.dumps(safe_params, ensure_ascii=False)

    conn = _get_conn()
    try:
        cur = conn.execute(
            """
            INSERT INTO experiment_records (page_url, page_title, params_json, explanation, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (page_url, page_title, params_json, explanation, note, created_at),
        )
        conn.commit()
        record_id = cur.lastrowid
        row = conn.execute(
            "SELECT * FROM experiment_records WHERE id = ?",
            (record_id,),
        ).fetchone()
        return _row_to_dict(row)
    finally:
        conn.close()


def list_records(limit: int = 100, query: str = "") -> list[dict[str, Any]]:
    limit = max(1, min(int(limit), 1000))
    conn = _get_conn()
    try:
        q = (query or "").strip()
        if q:
            like = f"%{q}%"
            rows = conn.execute(
                """
                SELECT * FROM experiment_records
                WHERE page_title LIKE ? OR page_url LIKE ? OR explanation LIKE ? OR note LIKE ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (like, like, like, like, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM experiment_records ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]
    finally:
        conn.close()


def get_record(record_id: int) -> dict[str, Any] | None:
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM experiment_records WHERE id = ?",
            (int(record_id),),
        ).fetchone()
        if row is None:
            return None
        return _row_to_dict(row)
    finally:
        conn.close()


def delete_record(record_id: int) -> bool:
    conn = _get_conn()
    try:
        cur = conn.execute("DELETE FROM experiment_records WHERE id = ?", (int(record_id),))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def clear_records() -> int:
    conn = _get_conn()
    try:
        cur = conn.execute("DELETE FROM experiment_records")
        conn.commit()
        return int(cur.rowcount or 0)
    finally:
        conn.close()


def update_record_note(record_id: int, note: str) -> dict[str, Any] | None:
    conn = _get_conn()
    try:
        conn.execute(
            "UPDATE experiment_records SET note = ? WHERE id = ?",
            (note, int(record_id)),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM experiment_records WHERE id = ?",
            (int(record_id),),
        ).fetchone()
        if row is None:
            return None
        return _row_to_dict(row)
    finally:
        conn.close()


def export_records_csv(limit: int = 1000) -> str:
    records = list_records(limit=limit)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "page_url", "page_title", "params_json", "explanation", "note", "created_at"])

    for rec in records:
        writer.writerow(
            [
                rec["id"],
                rec["page_url"],
                rec["page_title"],
                json.dumps(rec["params"], ensure_ascii=False),
                rec["explanation"],
                rec["note"],
                rec["created_at"],
            ]
        )

    csv_text = output.getvalue()
    output.close()
    # BOM helps Excel read UTF-8 Chinese correctly.
    return "\ufeff" + csv_text
