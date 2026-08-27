# Disc Golf Course Tracker

A CLI app for tracking disc golf courses, rounds, and stats — fully built,
no external services or API keys needed.

## Status: complete and working

Tested end-to-end (course creation, round logging, history, and stats).

## Features

- **Courses** — add courses with per-hole par and optional distance
- **Rounds** — log a round hole-by-hole, with date and optional notes
- **History** — see every round played, with score vs. par
- **Stats** — average vs. par per course, best round, an improving/trending
  read comparing your earlier rounds to your more recent ones, and your
  toughest hole overall (across all courses)

## Requirements

- Python 3 (no external packages — standard library only)

## Running it

```bash
python3 disc_golf_tracker.py
```

That's it. On first run it creates a `discgolf.db` SQLite file in the same
folder as the script — that's where all your data lives. Delete that file
any time to start fresh.

You'll get a menu:

```
========================================
   DISC GOLF COURSE TRACKER
========================================
 1. Add a course
 2. View courses
 3. Log a round
 4. View round history
 5. View stats
 6. Delete a course
 0. Quit
========================================
```

Suggested first run: add a course (option 1), log a round or two on it
(option 3), then check option 5 for stats.

## Notes

- Deleting a course also deletes its holes and any rounds logged on it —
  it'll ask for confirmation first.
- The database is just a local SQLite file, so it's portable — copy
  `discgolf.db` anywhere along with the script and your data comes with it.
