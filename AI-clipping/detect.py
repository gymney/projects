"""
v1 detection: no ML, just audio loudness. We stream the file's audio through
ffmpeg as raw 16-bit PCM (mono, downsampled to config.AUDIO_SAMPLE_RATE),
compute RMS loudness per short window, and flag windows that spike well
above their *local* baseline (so a loud stream overall doesn't just get
flagged wholesale, and a quiet stream's normal talking doesn't drown out
real spikes).

This runs in one streaming pass so a 3-5hr file doesn't need to be loaded
into memory at once.
"""
import subprocess
import numpy as np

import config


def extract_loudness_envelope(video_path):
    """Returns a numpy array of dBFS-ish RMS values, one per WINDOW_SECONDS,
    covering the whole file. Streams ffmpeg output rather than buffering
    the whole decoded audio track."""
    sr = config.AUDIO_SAMPLE_RATE
    window_samples = int(sr * config.WINDOW_SECONDS)
    bytes_per_sample = 2  # s16le

    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn",  # no video
        "-ac", "1",  # mono
        "-ar", str(sr),
        "-f", "s16le",
        "-loglevel", "error",
        "-",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    levels = []
    read_size = window_samples * bytes_per_sample
    leftover = b""
    while True:
        chunk = proc.stdout.read(read_size)
        if not chunk:
            break
        data = leftover + chunk
        usable_len = (len(data) // bytes_per_sample) * bytes_per_sample
        usable, leftover = data[:usable_len], data[usable_len:]
        if not usable:
            continue
        samples = np.frombuffer(usable, dtype=np.int16).astype(np.float32)
        rms = np.sqrt(np.mean(samples ** 2)) + 1e-6
        db = 20 * np.log10(rms / 32768.0)
        levels.append(db)

    proc.stdout.close()
    stderr = proc.stderr.read()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extraction failed: {stderr.decode(errors='ignore')}")

    return np.array(levels, dtype=np.float32)


def find_candidate_segments(levels):
    """Given the per-window dB levels, return a list of (start_sec, end_sec)
    candidate highlight segments."""
    if len(levels) == 0:
        return []

    window = config.WINDOW_SECONDS
    baseline_n = config.BASELINE_WINDOW

    # Rolling local baseline (median is more robust to spikes than mean)
    baseline = np.copy(levels)
    half = baseline_n // 2
    padded = np.pad(levels, (half, half), mode="edge")
    for i in range(len(levels)):
        baseline[i] = np.median(padded[i:i + baseline_n])

    spike_mask = levels > (baseline + config.PEAK_THRESHOLD_DB)
    spike_indices = np.nonzero(spike_mask)[0]

    if len(spike_indices) == 0:
        return []

    # Merge nearby spike windows into segments, then pad and cap length
    min_gap_windows = max(1, int(config.MIN_GAP_SECONDS / window))
    segments = []
    seg_start = spike_indices[0]
    prev = spike_indices[0]
    for idx in spike_indices[1:]:
        if idx - prev > min_gap_windows:
            segments.append((seg_start, prev))
            seg_start = idx
        prev = idx
    segments.append((seg_start, prev))

    total_duration = len(levels) * window
    results = []
    for start_idx, end_idx in segments:
        start = max(0.0, start_idx * window - config.PRE_PADDING)
        end = min(total_duration, end_idx * window + config.POST_PADDING)
        if end - start > config.MAX_CLIP_SECONDS:
            # keep it centered on the spike rather than dropping it entirely
            mid = (start + end) / 2
            start = max(0.0, mid - config.MAX_CLIP_SECONDS / 2)
            end = start + config.MAX_CLIP_SECONDS
        if end - start >= config.MIN_CLIP_SECONDS:
            results.append((round(start, 2), round(end, 2)))

    return results
