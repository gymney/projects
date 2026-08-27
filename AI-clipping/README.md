# AI Video Clipping Tool

A tool to help process and sort a large backlog of gameplay clips (Rocket
League) into usable content.

## Concept

- There's an existing backlog of roughly 2,000–5,000 unsorted Rocket League
  clips that need sorting into categories, plus a steady stream of new clips
  coming in.
- This tool's job: reduce the manual grind of scrubbing through raw footage
  by using AI to help identify, tag, and cut the clips worth keeping.
- Natural fit for the content-creation track — the output feeds directly into
  the video backlog used for editing and posting.

## Suggested tech stack

- **Language:** Python
- **Video handling:** `ffmpeg` (via `ffmpeg-python` or subprocess calls) for
  cutting/trimming clips
- **Detection/highlighting:** depending on ambition —
  - Simple version: scene-change or audio-peak detection (e.g. spikes in
    volume/excitement) to flag likely highlight moments
  - More ambitious version: a vision model or Whisper-based audio transcript
    to find moments worth clipping (goals, saves, callouts)
- **Storage:** local filesystem to start; a simple SQLite index of
  clip → tags → source file is enough to avoid re-processing the same footage

## Suggested starting scope

1. **Ingest** — point the tool at a folder of raw footage or existing clips.
2. **Detect** — flag candidate highlight moments (start simple: audio peaks
   or scene changes; refine later).
3. **Cut** — use ffmpeg to export flagged moments as short clips.
4. **Tag/sort** — bucket clips into categories (the same category tiers
   already used for the manual backlog sort) so they land pre-organized.
5. **Review queue** — a lightweight way to quickly approve/reject what the
   tool flagged, since automated detection won't be perfect early on.

## Getting started

```bash
pip install ffmpeg-python
# ffmpeg itself must also be installed on the system (not just the Python package)
```

## Open questions to resolve when picking this back up

- Is the goal full automation, or a tool that assists a human doing the final
  cut/selection?
- Should this work on the existing backlog first, or on new footage as it
  comes in (probably start with new footage — the backlog is a bigger, messier
  problem)?
- How much value would come from transcript/audio-based detection vs. just
  starting with simple heuristics
