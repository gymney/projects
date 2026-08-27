"""
Central config. Tweak these instead of hunting through the other files.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INCOMING_DIR = os.path.join(BASE_DIR, "incoming")      # drop/record files here (or watched folder)
PROCESSING_DIR = os.path.join(BASE_DIR, "processing")  # files currently being processed (in-progress guard)
CANDIDATES_DIR = os.path.join(BASE_DIR, "candidates")  # auto-cut clips waiting for your review
APPROVED_DIR = os.path.join(BASE_DIR, "approved")      # approved clips, sorted into category subfolders
REJECTED_DIR = os.path.join(BASE_DIR, "rejected")      # rejected clips (kept for a bit, not deleted outright)
DB_PATH = os.path.join(BASE_DIR, "clips.db")

for d in (INCOMING_DIR, PROCESSING_DIR, CANDIDATES_DIR, APPROVED_DIR, REJECTED_DIR):
    os.makedirs(d, exist_ok=True)

# Video extensions the watcher/upload will pick up
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".flv", ".avi", ".ts"}

# Categories for sorting approved clips. Edit this list to match your
# existing manual-sort tiers — this is just a placeholder default.
CATEGORIES = ["goals", "saves", "funny", "fails", "other"]

# --- "is this file still being recorded" guard ---
# We poll file size every STABLE_CHECK_INTERVAL seconds, and only start
# processing once the size hasn't changed for STABLE_CHECK_COUNT checks in
# a row. For a 3-5hr OBS/Streamlabs recording this comfortably avoids
# grabbing a file mid-write.
STABLE_CHECK_INTERVAL = 10   # seconds between size checks
STABLE_CHECK_COUNT = 3       # consecutive stable checks required

# --- detection tuning (audio-peak v1) ---
# We sample audio loudness in short windows across the whole file and flag
# windows that spike above the file's own rolling baseline. This is meant
# to catch "something exciting happened" (goal horn, callout, laughing,
# yelling) without any ML — cheap enough to run on a multi-hour file.
AUDIO_SAMPLE_RATE = 8000      # downsampled rate for analysis (speed, not quality)
WINDOW_SECONDS = 0.5          # RMS window size
BASELINE_WINDOW = 120         # how many windows (~60s) form the local "normal volume" baseline
PEAK_THRESHOLD_DB = 9.0       # how many dB above local baseline counts as a "spike"
MIN_GAP_SECONDS = 8.0         # peaks closer than this get merged into one clip
PRE_PADDING = 6.0             # seconds to include before a detected peak
POST_PADDING = 10.0           # seconds to include after a detected peak
MAX_CLIP_SECONDS = 45.0       # hard cap so merged spikes don't produce a 5-minute "clip"
MIN_CLIP_SECONDS = 3.0        # discard anything shorter than this (noise)
