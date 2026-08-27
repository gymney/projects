# Disc Golf Course Tracker — Web GUI

A Flask web front end over the same disc golf tracker, styled to match the
mini game suite (parchment/gold/indigo theme).

## Status: complete and tested

Every route tested end-to-end (add course, log round, history, stats,
delete course + cascade).

## Requirements

```bash
pip install flask
```

## Running it

```bash
python3 app.py
```

Then open **http://127.0.0.1:5000** in a browser.

On first run it creates a `discgolf.db` SQLite file in this folder — same
format as the CLI version, so the two are compatible with each other if you
ever want to switch between them (just point them at the same folder).

## What's in here

```
app.py              - Flask routes and page logic
tracker_core.py      - shared DB schema/setup (used by app.py)
templates/           - Jinja2 HTML templates (one per page)
static/style.css     - all styling
```

## Pages

- **Courses** (`/`) — list courses, add new ones, delete existing ones
- **Log Round** (`/rounds/log`) — pick a course, enter a score per hole
- **History** (`/history`) — every round logged, with score vs. par
- **Stats** (`/stats`) — per-course averages, best rounds, trend, and
  toughest hole overall

## Notes

- `app.secret_key` is a hardcoded dev value — fine for local use, but if this
  ever gets deployed anywhere reachable by others, swap it for a real secret.
- Deleting a course cascades to its holes and rounds (confirmed via a JS
  confirm dialog before submitting).
- `debug=True` is on in `app.py` for local development — turn it off before
  running this anywhere other than your own machine.
