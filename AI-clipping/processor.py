"""
Shared pipeline used by both the folder watcher and the manual upload route.
Takes one source video, runs detection, cuts candidate clips, records them
in the DB. Never touches a file that's still growing (see watcher.py for
the stability check that happens before this is called).
"""
import os
import time
import uuid

import config
import db
import detect
import cutter
from logs import log


def process_file(source_path):
    file_hash = db.hash_file(source_path)
    if db.is_processed(file_hash):
        log(f"[skip] already processed: {source_path}")
        return []

    log(f"[processing] {source_path}")
    levels = detect.extract_loudness_envelope(source_path)
    segments = detect.find_candidate_segments(levels)
    log(f"[processing] found {len(segments)} candidate segment(s)")

    base_name = os.path.splitext(os.path.basename(source_path))[0]
    created_clip_ids = []

    cut_start_time = time.monotonic()
    last_log_time = cut_start_time
    log_interval = 10.0

    for i, (start, end) in enumerate(segments, start=1):
        clip_filename = f"{base_name}__{start:.1f}-{end:.1f}__{uuid.uuid4().hex[:6]}.mp4"
        clip_path = os.path.join(config.CANDIDATES_DIR, clip_filename)
        try:
            cutter.cut_clip(source_path, start, end, clip_path)
        except RuntimeError as e:
            log(f"[error] cutting {source_path} [{start}-{end}]: {e}")
            continue
        clip_id = db.add_clip(source_path, file_hash, start, end, clip_path)
        created_clip_ids.append(clip_id)

        now = time.monotonic()
        if now - last_log_time >= log_interval or i == len(segments):
            elapsed = now - cut_start_time
            log(f"[processing] cut {i}/{len(segments)} clip(s) so far ({elapsed:.0f}s elapsed)")
            last_log_time = now

    db.mark_processed(file_hash, source_path)
    log(f"[processing] done -- {len(created_clip_ids)} clip(s) ready for review: {source_path}")
    return created_clip_ids
