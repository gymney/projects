# Mini Game Suite

A small collection of collaborative browser minigames, built as a shared
learning project.

## Status: two games already built

### 1. Rune Match (`rune-match.html`)
A card-flipping memorization game on a 4x5 grid (10 pairs). Flip tiles to
find matching sigils, tracked with a move counter, timer, and a
session-only best score. Fantasy/grimoire visual theme (parchment, gold,
deep indigo).

### 2. Shortcut Sigils (`shortcut-sigils.html`)
A keyboard shortcuts quiz game with five sub-games ("realms"): Excel,
Discord, Word, Confluence, and General PC. Each realm runs 8 multiple-choice
rounds pulled from a shuffled question bank, with score and streak tracking.
Same visual language as Rune Match so the two feel like one suite.

Both are single self-contained HTML files — no build step, no dependencies,
just open in a browser.

### 3. (a third idea — details forgotten)
There was a third minigame idea mentioned that didn't get captured before it
was lost. Worth jotting down next time it's remembered so it doesn't get
lost again.

## Suggested next steps

- Decide whether these stay standalone HTML files or get pulled into a
  single suite shell (a small landing page linking out to each game, still
  no backend needed).
- If a persistent leaderboard/best-score feature is wanted across sessions,
  that's the point where a lightweight backend (Python/FastAPI + SQLite,
  consistent with the rest of the roadmap's Python pivot) would come in —
  right now both games only track scores in memory for the current session.
- Once the third game idea is recovered, add it here and decide whether it
  fits the same visual theme or wants its own identity.

## Suggested tech stack (if it grows past static HTML)

- **Backend (optional, for shared/persistent scores):** Python, FastAPI,
  SQLite
- **Frontend:** stays plain HTML/CSS/JS — no framework needed for games this
  size
