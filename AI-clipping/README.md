# AI Video Clipping Tool ("Clip Finder")

A local tool that watches for gameplay recordings (or takes an upload),
automatically detects and cuts likely highlight moments, and gives you a
simple web UI to approve or reject each candidate clip before it lands in a
sorted folder.

## Status: built and tested end-to-end

Detection, cutting, dedup, the folder watcher, and the full Flask
review/approve/reject workflow have all been run against a real (synthetic)
test video and verified to behave correctly, including:

- Audio-peak detection correctly flags loudness spikes and ignores quiet
  stretches
- Cut clips come out at the expected start/end times and duration
- The same source file is never processed twice (hash-based dedup)
- The folder watcher correctly waits out a file that's still being written
  before touching it, and doesn't grab a mid-recording file early
- The watcher and the browser upload path share the same `incoming/`
  folder, so an uploaded file also gets independently noticed by the
  watcher — confirmed this is harmless (the dedup guard skips it) but was
  previously wasteful, since the watcher would keep re-noticing an already-
  processed file left sitting in `incoming/` and re-run its whole 30-second
  stability wait every ~5 seconds, forever. **Fixed** — see Known issues
  below.
- Approve/reject correctly moves the clip file to `approved/<category>/` or
  `rejected/`, and updates its stored path and status in the database
- The review queue, history page, and media (video) serving routes all
  render/respond correctly

## Concept

- There's an existing backlog of roughly 2,000–5,000 unsorted Rocket League
  clips that need sorting into categories, plus a steady stream of new clips
  coming in.
- This tool reduces the manual grind of scrubbing through raw footage by
  using a simple audio-loudness heuristic to flag likely highlight moments,
  cut them into short candidate clips, and let you quickly approve or reject
  each one from a browser tab.
- Two ways to get footage in:
  - Drop a finished recording into the watched `incoming/` folder (e.g.
    point your OBS/Streamlabs output there) — the watcher waits until the
    file stops growing before processing it.
  - Upload a file directly through the web page.

## How it works

1. **Ingest** — a file lands in `incoming/`, either via the folder watcher
   or a browser upload.
2. **Detect** (`detect.py`) — audio is streamed through ffmpeg, RMS loudness
   is measured in short windows across the whole file, and windows that
   spike well above their *local* baseline are flagged as candidate
   highlights. No ML — cheap enough to run on a multi-hour file.
3. **Cut** (`cutter.py`) — each flagged window (with a few seconds of
   padding before/after) is re-encoded out as its own short clip in
   `candidates/`.
4. **Review** — the web UI lists every pending candidate clip with a
   built-in video player. Approve (picking a category) or reject each one.
5. **Sort** — approved clips move to `approved/<category>/`; rejected clips
   move to `rejected/` (kept, not deleted).

## Tech stack

- **Language:** Python
- **Video/audio:** ffmpeg (via subprocess), numpy for the loudness math
- **Web UI:** Flask, Jinja2 templates
- **Storage:** SQLite (tracks processed source files and every candidate
  clip's status)

## Requirements

- Python 3
- `ffmpeg` installed and on your system PATH (not just the Python wrapper)

```bash
pip install flask numpy
```

## Running it

```bash
python3 app.py
```

Then open **http://127.0.0.1:5000**. This starts the Flask server *and* the
background folder watcher in one process — nothing else needs to run
separately.

- Drop recordings into the `incoming/` folder (created automatically next
  to the script), or use the upload box on the review page.
- Review queue is the home page — approve or reject each candidate as it
  shows up.
- History page shows everything already approved/rejected.

All settings (folder paths, video extensions, category list, and detection
tuning — sensitivity, clip padding, min/max clip length) live in
`config.py`.

## Known issues / recent fixes

- **Fixed:** the folder watcher previously forgot that it had already
  handled a file once its processing thread finished, so if that file
  stayed in `incoming/` (which it always does — nothing moves it out), the
  watcher would re-detect it on every scan and re-run the full stability
  wait indefinitely. It now only re-queues a file for another look if
  something actually went wrong processing it (so transient errors can
  still retry); a successfully handled file is left alone for good.
- **Not yet handled:** processed files are never moved out of `incoming/`
  automatically. This isn't harmful (dedup prevents reprocessing) but the
  folder will just keep growing — worth adding a step that moves or deletes
  source files once they're fully processed.

## Open questions to resolve going forward

- Is the goal full automation, or a tool that assists a human doing the
  final cut/selection? (Currently built as the latter — everything goes
  through manual review.)
- Detection is pure audio-peak heuristics right now. Worth revisiting
  whether transcript/audio-keyword detection (e.g. Whisper picking up
  callouts) or a vision model would meaningfully improve what gets flagged,
  versus just tuning the existing thresholds.
- Should there be a way to process the *existing* clip backlog through this
  tool, or is it meant purely for new footage going forward?
