"""
Cuts a (start, end) segment out of a source video into its own file.

Uses NVIDIA NVENC for video encoding so the RTX 5070 Ti handles the
encode instead of the CPU. The video is still re-encoded rather than
stream-copied, preserving frame-accurate start/end cuts.
"""

import os
import subprocess


def cut_clip(source_path, start, end, output_path):
    duration = max(0.1, end - start)

    cmd = [
        "ffmpeg",
        "-y",

        # Seek before decoding the input. The output is still re-encoded,
        # so FFmpeg can produce an accurate cut rather than relying on
        # keyframes as it would with -c copy.
        "-ss", f"{start:.2f}",
        "-i", source_path,
        "-t", f"{duration:.2f}",

        # NVIDIA hardware H.264 encoding.
        "-c:v", "h264_nvenc",

        # Quality-based VBR encoding.
        "-preset", "p5",
        "-tune", "hq",
        "-rc", "vbr",
        "-cq", "20",
        "-b:v", "0",

        # Keep normal-ish compatibility for the resulting clips.
        "-pix_fmt", "yuv420p",

        # Audio remains CPU-side, but this is trivial compared to video
        # encoding.
        "-c:a", "aac",
        "-b:a", "128k",

        "-movflags", "+faststart",

        "-loglevel", "error",
        output_path,
    ]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    result = subprocess.run(cmd, capture_output=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg cut failed: {result.stderr.decode(errors='ignore')}"
        )

    return output_path