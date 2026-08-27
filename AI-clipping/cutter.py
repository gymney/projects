"""
Cuts a (start, end) segment out of a source video into its own file.

We re-encode (rather than -c copy) because candidate clips are short
(seconds, not hours) so the encode cost is trivial, and stream-copy cutting
is only accurate to the nearest keyframe -- which can chop a highlight
awkwardly. Re-encoding gives frame-accurate cuts.
"""
import subprocess
import os


def cut_clip(source_path, start, end, output_path):
    duration = max(0.1, end - start)
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start:.2f}",
        "-i", source_path,
        "-t", f"{duration:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "128k",
        "-loglevel", "error",
        output_path,
    ]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg cut failed: {result.stderr.decode(errors='ignore')}")
    return output_path
