"""
Shared database setup for the Disc Golf Course Tracker.
Used by both the CLI (tracker.py) and the web GUI (app.py).
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "discgolf.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            location TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS holes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            hole_number INTEGER NOT NULL,
            par INTEGER NOT NULL,
            distance_ft INTEGER,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE(course_id, hole_number)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            played_on TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_id INTEGER NOT NULL,
            hole_number INTEGER NOT NULL,
            strokes INTEGER NOT NULL,
            FOREIGN KEY (round_id) REFERENCES rounds(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
