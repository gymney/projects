"""
Shared pipeline used by both the folder watcher and the manual upload route.
Takes one source video, runs detection, cuts candidate clips, records them
in the DB. Never touches a file that's still growing (see watcher.py for
the stability check that happens before this is called).
"""
import os
import uuid

import config
import db
import detect
import cutter


def process_file(source_path):
    file_hash = db.hash_file(source_path)
    if db.is_processed(file_hash):
        print(f"[skip] already processed: {source_path}")
        return []

    print(f"[processing] {source_path}")
    levels = detect.extract_loudness_envelope(source_path)
    segments = detect.find_candidate_segments(levels)
    print(f"[processing] found {len(segments)} candidate segment(s)")

    base_name = os.path.splitext(os.path.basename(source_path))[0]
    created_clip_ids = []

    for start, end in segments:
        clip_filename = f"{base_name}__{start:.1f}-{end:.1f}__{uuid.uuid4().hex[:6]}.mp4"
        clip_path = os.path.join(config.CANDIDATES_DIR, clip_filename)
        try:
            cutter.cut_clip(source_path, start, end, clip_path)
        except RuntimeError as e:
            print(f"[error] cutting {source_path} [{start}-{end}]: {e}")
            continue
        clip_id = db.add_clip(source_path, file_hash, start, end, clip_path)
        created_clip_ids.append(clip_id)

    db.mark_processed(file_hash, source_path)
    return created_clip_ids
