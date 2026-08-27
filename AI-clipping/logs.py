"""
Tiny shared logging buffer. Every module calls log(...) instead of print()
so the same lines show up both in the console AND in the web UI's
collapsible log panel (via the /api/logs route in app.py).

Kept deliberately simple -- an in-memory ring buffer, not a real logging
framework. Good enough for a local single-process tool; log history is lost
on restart, which is fine here.
"""
import threading
import time
from collections import deque

_lock = threading.Lock()
_buffer = deque(maxlen=1000)


def log(message):
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {message}"
    print(line, flush=True)
    with _lock:
        _buffer.append(line)


def get_recent(n=300):
    with _lock:
        return list(_buffer)[-n:]
