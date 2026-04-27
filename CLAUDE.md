# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack
- **Frontend**: Vue 3 + Vite + Tailwind CSS + Vue Router + Axios
- **Backend**: Python FastAPI + SQLAlchemy + SQLite
- **TTS**: Browser Web Speech API + edge-tts for server-side

## Build & Run
- 重启服务服务时不要关闭其他端口的服务，仅重启后端9000端口，前端5173端口！

```bash
# Backend (port 9000)
cd /home/xsq/happy-learning && python3 -m uvicorn app.main:app --port 9000

# Frontend dev (port 5173)
cd /home/xsq/happy-learning/frontend && npm run dev

# Frontend build (served by FastAPI in production)
cd /home/xsq/happy-learning/frontend && npm run build
```

## Content Scripts
- `scripts/generate_questions.py` — 生成 Big Muzzy 题库（6种题型），从 MUZZY_DATA 配置生成
- `scripts/import_muzzy_cards.py` — 导入 Muzzy 单词图卡到数据库
- `scripts/import_yakka_dee.py` — 导入 Yakka Dee 单词图卡
- `scripts/import_nc_english.py` — 导入新概念英语内容

## Architecture

### Data Model
- **Textbook** → contains Units + VocabWords
- **Unit** → contains Questions + VocabWords, has video_path
- **Question** → 6 types: `image_select_word`, `image_select_sentence`, `listen_select`, `listen_spell`, `listen_spell_sentence`, `image_listen_spell_sentence`
- **User** → has avatar (emoji), Scores, DailyProgress, UnitProgress
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