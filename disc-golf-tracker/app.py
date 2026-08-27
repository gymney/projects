#!/usr/bin/env python3
"""
Disc Golf Course Tracker - Web GUI
------------------------------------
Flask front end over the same SQLite schema as the CLI version.
Run with: python3 app.py, then open http://127.0.0.1:5000
"""

import os
import statistics
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash

from tracker_core import get_conn, init_db

app = Flask(__name__)
app.secret_key = "disc-golf-tracker-dev-key"  # fine for local-only use


# ---------------------------------------------------------------------------
# Data access helpers (return plain data, no printing/input — web-friendly)
# ---------------------------------------------------------------------------

def fetch_courses():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.location,
               COUNT(h.id) as hole_count,
               COALESCE(SUM(h.par), 0) as total_par
        FROM courses c
        LEFT JOIN holes h ON h.course_id = c.id
        GROUP BY c.id
        ORDER BY c.name
    """)
    rows = cur.fetchall()
    conn.close()
    return [
        {"id": r[0], "name": r[1], "location": r[2], "hole_count": r[3], "total_par": r[4]}
        for r in rows
    ]


def fetch_course(course_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, location FROM courses WHERE id=?", (course_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    cur.execute("SELECT hole_number, par, distance_ft FROM holes WHERE course_id=? ORDER BY hole_number", (course_id,))
    holes = [{"hole_number": h[0], "par": h[1], "distance_ft": h[2]} for h in cur.fetchall()]
    conn.close()
    return {"id": row[0], "name": row[1], "location": row[2], "holes": holes}


def fetch_rounds():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, r.played_on, c.name, r.notes, c.id
        FROM rounds r JOIN courses c ON r.course_id = c.id
        ORDER BY r.played_on DESC, r.id DESC
    """)
    rounds = []
    for round_id, played_on, course_name, notes, course_id in cur.fetchall():
        cur.execute("SELECT SUM(strokes) FROM scores WHERE round_id=?", (round_id,))
        total_strokes = cur.fetchone()[0] or 0
        cur.execute("SELECT SUM(par) FROM holes WHERE course_id=?", (course_id,))
        total_par = cur.fetchone()[0] or 0
        diff = total_strokes - total_par
        rounds.append({
            "id": round_id, "played_on": played_on, "course_name": course_name,
            "notes": notes, "total_strokes": total_strokes, "total_par": total_par,
            "diff": diff, "diff_str": fmt_diff(diff),
        })
    conn.close()
    return rounds


def fmt_diff(diff):
    if diff > 0:
        return f"+{diff}"
    if diff < 0:
        return str(diff)
    return "E"


def compute_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM rounds")
    round_count = cur.fetchone()[0]
    if round_count == 0:
        conn.close()
        return {"round_count": 0, "courses": [], "toughest_hole": None}

    cur.execute("SELECT id, name FROM courses ORDER BY name")
    courses_raw = cur.fetchall()

    course_stats = []
    for course_id, course_name in courses_raw:
        cur.execute("SELECT id, played_on FROM rounds WHERE course_id=? ORDER BY played_on", (course_id,))
        rounds = cur.fetchall()
        if not rounds:
            continue
        diffs = []
        for round_id, played_on in rounds:
            cur.execute("SELECT SUM(strokes) FROM scores WHERE round_id=?", (round_id,))
            total_strokes = cur.fetchone()[0] or 0
            cur.execute("SELECT SUM(par) FROM holes WHERE course_id=?", (course_id,))
            total_par = cur.fetchone()[0] or 0
            diffs.append((played_on, total_strokes, total_par, total_strokes - total_par))

        best = min(diffs, key=lambda d: d[3])
        avg_diff = statistics.mean(d[3] for d in diffs)
        trend_label = None
        trend_val = None
        if len(diffs) >= 2:
            first_half = diffs[: len(diffs) // 2]
            second_half = diffs[len(diffs) // 2:]
            trend_val = statistics.mean(d[3] for d in second_half) - statistics.mean(d[3] for d in first_half)
            trend_label = "improving" if trend_val < 0 else "trending up" if trend_val > 0 else "steady"

        course_stats.append({
            "name": course_name,
            "round_count": len(diffs),
            "avg_diff": avg_diff,
            "best_strokes": best[1],
            "best_diff_str": fmt_diff(best[3]),
            "best_date": best[0],
            "trend_label": trend_label,
            "trend_val": trend_val,
        })

    cur.execute("""
        SELECT c.name, h.hole_number, h.par, AVG(s.strokes - h.par) as avg_over
        FROM scores s
        JOIN rounds r ON s.round_id = r.id
        JOIN holes h ON h.course_id = r.course_id AND h.hole_number = s.hole_number
        JOIN courses c ON c.id = r.course_id
        GROUP BY c.id, h.hole_number
        ORDER BY avg_over DESC
        LIMIT 1
    """)
    toughest_row = cur.fetchone()
    toughest = None
    if toughest_row:
        toughest = {
            "course_name": toughest_row[0], "hole_number": toughest_row[1],
            "par": toughest_row[2], "avg_over": toughest_row[3],
        }

    conn.close()
    return {"round_count": round_count, "courses": course_stats, "toughest_hole": toughest}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html", courses=fetch_courses())


@app.route("/courses/add", methods=["GET", "POST"])
def add_course():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        try:
            num_holes = int(request.form.get("num_holes", "0"))
        except ValueError:
            num_holes = 0

        if not name or num_holes < 1:
            flash("Course name and a positive number of holes are required.", "error")
            return redirect(url_for("add_course"))

        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO courses (name, location) VALUES (?, ?)", (name, location))
        except Exception:
            conn.close()
            flash(f"A course named '{name}' already exists.", "error")
            return redirect(url_for("add_course"))
        course_id = cur.lastrowid

        for h in range(1, num_holes + 1):
            par = request.form.get(f"par_{h}", "3")
            dist = request.form.get(f"dist_{h}", "")
            par = int(par) if str(par).isdigit() else 3
            dist = int(dist) if str(dist).isdigit() else None
            cur.execute(
                "INSERT INTO holes (course_id, hole_number, par, distance_ft) VALUES (?, ?, ?, ?)",
                (course_id, h, par, dist),
            )
        conn.commit()
        conn.close()
        flash(f"Saved '{name}' with {num_holes} holes.", "success")
        return redirect(url_for("home"))

    # GET: how many holes to build the form for (defaults to 18, adjustable via query param)
    try:
        num_holes = int(request.args.get("holes", 18))
    except ValueError:
        num_holes = 18
    num_holes = max(1, min(num_holes, 36))
    return render_template("add_course.html", num_holes=num_holes)


@app.route("/courses/<int:course_id>/delete", methods=["POST"])
def delete_course(course_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM courses WHERE id=?", (course_id,))
    row = cur.fetchone()
    if row:
        cur.execute("DELETE FROM courses WHERE id=?", (course_id,))
        conn.commit()
        flash(f"Deleted '{row[0]}'.", "success")
    conn.close()
    return redirect(url_for("home"))


@app.route("/rounds/log", methods=["GET", "POST"])
def log_round():
    courses = fetch_courses()

    if request.method == "POST":
        course_id = request.form.get("course_id")
        played_on = request.form.get("played_on") or date.today().isoformat()
        notes = request.form.get("notes", "").strip()

        course = fetch_course(course_id) if course_id else None
        if not course:
            flash("Pick a valid course.", "error")
            return redirect(url_for("log_round"))

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO rounds (course_id, played_on, notes) VALUES (?, ?, ?)",
                    (course_id, played_on, notes))
        round_id = cur.lastrowid

        for hole in course["holes"]:
            strokes_raw = request.form.get(f"strokes_{hole['hole_number']}", "")
            strokes = int(strokes_raw) if strokes_raw.isdigit() else hole["par"]
            cur.execute("INSERT INTO scores (round_id, hole_number, strokes) VALUES (?, ?, ?)",
                        (round_id, hole["hole_number"], strokes))
        conn.commit()
        conn.close()
        flash(f"Round saved for {course['name']} on {played_on}.", "success")
        return redirect(url_for("history"))

    selected_course_id = request.args.get("course_id")
    selected_course = fetch_course(selected_course_id) if selected_course_id else None
    return render_template(
        "log_round.html",
        courses=courses,
        selected_course=selected_course,
        today=date.today().isoformat(),
    )


@app.route("/history")
def history():
    return render_template("history.html", rounds=fetch_rounds())


@app.route("/stats")
def stats():
    return render_template("stats.html", stats=compute_stats())


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
