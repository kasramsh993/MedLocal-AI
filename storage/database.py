from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "medlocal.db"


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS approved_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT,
                patient_date_of_birth TEXT,
                patient_insurance TEXT,
                doctor_name TEXT,
                specialty TEXT,
                original_transcript TEXT,
                corrected_transcript TEXT,
                generated_report TEXT,
                final_report TEXT,
                icd10_codes TEXT,
                goz_codes TEXT,
                billing_codes TEXT,
                model_name TEXT,
                created_at TEXT,
                approved_at TEXT,
                pdf_path TEXT,
                status TEXT
            )
            """
        )
        existing = {row[1] for row in conn.execute("PRAGMA table_info(approved_reports)").fetchall()}
        if "billing_codes" not in existing:
            conn.execute("ALTER TABLE approved_reports ADD COLUMN billing_codes TEXT")


def save_approved_report(report_data: dict[str, Any]) -> int:
    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    row = {
        "patient_name": report_data.get("patient_name", ""),
        "patient_date_of_birth": report_data.get("patient_date_of_birth", ""),
        "patient_insurance": report_data.get("patient_insurance", ""),
        "doctor_name": report_data.get("doctor_name", ""),
        "specialty": report_data.get("specialty", ""),
        "original_transcript": report_data.get("original_transcript", ""),
        "corrected_transcript": report_data.get("corrected_transcript", ""),
        "generated_report": report_data.get("generated_report", ""),
        "final_report": report_data.get("final_report", ""),
        "icd10_codes": json.dumps(report_data.get("icd10_codes", []), ensure_ascii=False),
        "goz_codes": json.dumps(report_data.get("goz_codes", []), ensure_ascii=False),
        "billing_codes": json.dumps(report_data.get("billing_codes", []), ensure_ascii=False),
        "model_name": report_data.get("model_name", ""),
        "created_at": report_data.get("created_at", now),
        "approved_at": report_data.get("approved_at", now),
        "pdf_path": str(report_data.get("pdf_path", "")),
        "status": report_data.get("status", "Approved"),
    }
    columns = ", ".join(row.keys())
    placeholders = ", ".join("?" for _ in row)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            f"INSERT INTO approved_reports ({columns}) VALUES ({placeholders})",
            tuple(row.values()),
        )
        return int(cursor.lastrowid)


def update_report_pdf_path(report_id: int, pdf_path: Path | str) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE approved_reports SET pdf_path = ? WHERE id = ?",
            (str(pdf_path), report_id),
        )


def get_report_by_id(report_id: int) -> dict[str, Any] | None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM approved_reports WHERE id = ?", (report_id,)).fetchone()
        return dict(row) if row else None


def list_recent_reports(limit: int = 10) -> list[dict[str, Any]]:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM approved_reports ORDER BY approved_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
