# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack
- **Frontend**: Vue 3 + Vite + Tailwind CSS + Vue Router + Axios
- **Backend**: Python FastAPI + SQLAlchemy + SQLite
- **TTS**: Browser Web Speech API + edge-tts for server-side

## Build & Run
```bash
# Backend (port 9000)
cd /home/xsq/happy-learning && python3 -m uvicorn app.main:app --port 9000

# Frontend dev (port 5173)
cd /home/xsq/happy-learning/frontend && npm run dev

# Frontend build (served by FastAPI in production)
cd /home/xsq/happy-learning/frontend && npm run build

# Seed/import data
PYTHONPATH=. python3 scripts/seed_data.py
PYTHONPATH=. python3 scripts/import_muzzy_cards.py
PYTHONPATH=. python3 scripts/import_yakka_dee.py
PYTHONPATH=. python3 scripts/import_nc_english.py
```

## Architecture

### Data Model
- **Textbook** → contains Units + VocabWords
- **Unit** → contains Questions + VocabWords, has video_path
- **Question** → 5 types: `image_select_word`, `image_select_sentence`, `listen_select`, `listen_spell`, `listen_spell_sentence`
- **User** → has Scores, DailyProgress, UnitProgress
- **VocabWord** → word with image_path and example_sentence

### Static Mounts
- `/muzzy_word_cards/` → `data/muzzy_word_cards/`
- `/yakka_dee/` → `data/yakka_dee/`
- `/` → `frontend/dist/` (production only)

### Frontend Routes
`/` (avatar select) → `/dashboard` → `/video/:unitId` → `/quiz/:unitId` → `/results`

### Key Routers
- `users` — user CRUD
- `courses` — textbooks listing (legacy alias in frontend)
- `questions` — by unit/textbook, quiz generation, word-to-image
- `scores` — record scores, unit completion, user scores
- `progress` — daily/unit progress tracking
- `media` — video streaming from `data/videos/`
- `tts` — text-to-speech endpoint

## Code Style
- Python: PEP 8, snake_case functions/variables
- Vue: `<script setup>` composition API, kebab-case components
- No comments unless WHY is non-obvious

## Conventions
- Use planning-with-files skill for multi-step tasks
- Phase-based development tracked in task_plan.md
- Content import scripts in `scripts/` for different sources (Muzzy, Yakka Dee, NC English)