"""
Tiny SQLite layer. Two tables:
  - processed_files: hash of every source file we've already run detection
    on, so re-running the watcher/app never double-processes a file.
  - clips: every candidate clip cut from a source file, with review status.
"""
import sqlite3
import hashlib
import contextlib
from datetime import datetime, timezone

import config


def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with contextlib.closing(get_conn()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_files (
                hash TEXT PRIMARY KEY,
                source_path TEXT NOT NULL,
                processed_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file TEXT NOT NULL,
                source_hash TEXT NOT NULL,
                start_time REAL NOT NULL,
                end_time REAL NOT NULL,
                clip_path TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | rejected
                category TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def hash_file(path, chunk_size=1024 * 1024 * 4):
    """Fast-ish hash: sample size + first/last few MB rather than hashing a
    5-hour file byte-for-byte. Good enough to dedupe, not a security hash."""
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        first = f.read(chunk_size)
        h.update(first)
        size += len(first)
        f.seek(0, 2)
        total_size = f.tell()
        if total_size > chunk_size:
            f.seek(max(0, total_size - chunk_size))
            last = f.read(chunk_size)
            h.update(last)
    h.update(str(total_size).encode())
    return h.hexdigest()


def is_processed(file_hash):
    with contextlib.closing(get_conn()) as conn:
        row = conn.execute(
            "SELECT 1 FROM processed_files WHERE hash = ?", (file_hash,)
        ).fetchone()
        return row is not None


def mark_processed(file_hash, source_path):
    with contextlib.closing(get_conn()) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO processed_files (hash, source_path, processed_at) VALUES (?, ?, ?)",
            (file_hash, source_path, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()


def add_clip(source_file, source_hash, start_time, end_time, clip_path):
    with contextlib.closing(get_conn()) as conn:
        cur = conn.execute(
            """INSERT INTO clips (source_file, source_hash, start_time, end_time, clip_path, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (source_file, source_hash, start_time, end_time, clip_path,
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return cur.lastrowid


def get_clip(clip_id):
    with contextlib.closing(get_conn()) as conn:
        return conn.execute("SELECT * FROM clips WHERE id = ?", (clip_id,)).fetchone()


def list_clips(status=None):
    with contextlib.closing(get_conn()) as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM clips WHERE status = ? ORDER BY created_at DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM clips ORDER BY created_at DESC").fetchall()
        return rows


def update_status(clip_id, status, category=None):
    with contextlib.closing(get_conn()) as conn:
        conn.execute(
            "UPDATE clips SET status = ?, category = ? WHERE id = ?",
            (status, category, clip_id),
        )
        conn.commit()
