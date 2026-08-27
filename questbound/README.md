# QuestBound

An RPG-style habit and goal tracker. Real-world tasks deal damage to bosses —
the more consistently you complete your goals, the faster the boss falls.

## Concept

- Completing real tasks deals damage to a "boss" tied to a goal or habit chain.
- Multiple play modes:
  - **Solo** — you vs. your own boss/goal.
  - **Duo** — two people share a boss, damage from either side counts.
  - **Party** — small group co-op against a shared boss.
  - **Server-wide** — a larger community goal everyone chips away at.
- Built on top of a structured goal-setting framework: long-horizon targets
  cascade down into daily tasks, and completing the daily tasks is what
  generates damage.
- This is the most conceptually developed project in the roadmap — the RPG
  mechanics and mode structure are already worked out; what's left is mostly
  implementation.

## Status

- Already has a real codebase in progress: a multi-service scaffold using
  **FastAPI**, **PostgreSQL**, **Docker**, **JWT auth**, and **SQLAlchemy**.
- Lives in a `SaaS` parent directory with two services so far:
  - `alx_hope` — the quest-service (boss/goal/damage logic)
  - `user_service` — auth and user accounts
- This is the active codebase for the Python/FastAPI self-teaching track —
  treat this README as a companion doc, not a replacement for that existing
  scaffold.

## Suggested tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL
- **Auth:** JWT
- **Infra:** Docker / docker-compose for local dev
- **Frontend:** not yet decided — could start as a simple API + CLI or basic
  web client before investing in a full frontend

## Core entities (starting point)

- `User` — account, auth
- `Goal` — a long-horizon target that cascades into tasks
- `Task` — a daily/recurring action tied to a goal
- `Boss` — HP pool tied to a goal, takes damage from completed tasks
- `Party` / `Group` — optional grouping of users sharing a boss

## Open questions to resolve when picking this back up

- How exactly task difficulty maps to damage dealt
- Whether server-wide mode needs its own service or just a `scope` field on
  `Boss`
- What "leveling up" or failure states look like (does a boss regenerate HP
  if you miss days?)
