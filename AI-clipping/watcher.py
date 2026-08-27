"""
Watches config.INCOMING_DIR for new video files (e.g. an OBS/Streamlabs
output folder) and kicks off processing once a file has stopped growing --
so a recording that's still in progress is left alone until it's done.

Runs as a background thread started from app.py, so `python app.py` is the
only thing you need to run.
"""
import os
import time
import threading

import config
from processor import process_file


def _is_video_file(path):
    return os.path.splitext(path)[1].lower() in config.VIDEO_EXTENSIONS


def _wait_until_stable(path):
    """Polls file size; returns True once it hasn't changed for
    STABLE_CHECK_COUNT consecutive checks, False if the file disappeared."""
    stable_count = 0
    last_size = -1
    while stable_count < config.STABLE_CHECK_COUNT:
        if not os.path.exists(path):
            return False
        try:
            size = os.path.getsize(path)
        except OSError:
            return False
        if size == last_size and size > 0:
            stable_count += 1
        else:
            stable_count = 0
        last_size = size
        time.sleep(config.STABLE_CHECK_INTERVAL)
    return True


def _watch_loop(stop_event):
    seen = set()
    print(f"[watcher] watching {config.INCOMING_DIR}")
    while not stop_event.is_set():
        try:
            for name in os.listdir(config.INCOMING_DIR):
                path = os.path.join(config.INCOMING_DIR, name)
                if path in seen or not os.path.isfile(path) or not _is_video_file(path):
                    continue
                seen.add(path)

                def handle(p=path):
                    print(f"[watcher] new file detected: {p} -- waiting for it to finish writing")
                    if _wait_until_stable(p):
                        try:
                            process_file(p)
                            # Successfully handled (or already-processed via the dedup
                            # guard in process_file) -- leave it in `seen` permanently
                            # so a file that's never moved out of INCOMING_DIR doesn't
                            # get re-detected and re-queued for a stability wait on
                            # every scan forever.
                            return
                        except Exception as e:
                            print(f"[watcher] error processing {p}: {e}")
                            # Fall through and discard so a transient error (e.g. a
                            # one-off ffmpeg hiccup) can be retried on the next scan.
                    else:
                        # File disappeared mid-wait -- also fine to retry if it reappears.
                        pass
                    seen.discard(p)

                threading.Thread(target=handle, daemon=True).start()
        except FileNotFoundError:
            pass
        time.sleep(5)


def start_watcher_thread():
    stop_event = threading.Event()
    t = threading.Thread(target=_watch_loop, args=(stop_event,), daemon=True)
    t.start()
    return stop_event
