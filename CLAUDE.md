# 快乐学英语 - Project Instructions

## Tech Stack
- **Frontend**: Vue 3 + Vite + Tailwind CSS + Vue Router + Axios
- **Backend**: Python FastAPI + SQLAlchemy + SQLite
- **TTS**: Browser Web Speech API

## Code Style
- Python: PEP 8, snake_case for functions/variables
- Vue: `<script setup>` composition API, kebab-case component names
- Frontend files in `frontend/src/`, backend in `app/`

## Build & Run
- **Backend**: `cd /home/xsq/happy-learning && python3 -m uvicorn app.main:app --port 9000`
- **Frontend dev**: `cd /home/xsq/happy-learning/frontend && npm run dev`
- **Seed data**: `PYTHONPATH=. python3 scripts/seed_data.py`
- **Frontend build**: `cd /home/xsq/happy-learning/frontend && npm run build`

## Project Structure
```
app/                  # FastAPI backend
  main.py             # Entry point
  database.py         # SQLAlchemy setup
  models/             # DB models
  routers/            # API endpoints
  services/           # Business logic
  schemas.py          # Pydantic schemas
frontend/src/         # Vue 3 frontend
  views/              # Page components
  components/         # Reusable components
  api/                # API client
data/                 # Database, videos, scripts
scripts/              # Helper scripts
```

## API Endpoints
- `GET/POST /api/users/` — User management
- `GET/POST /api/courses/` — Courses with units
- `GET/POST /api/units/` — Units
- `GET/POST /api/questions/` — Questions by unit
- `POST /api/scores/` — Record scores
- `POST /api/progress/` — Record daily progress

## Conventions
- Use planning-with-files skill for multi-step tasks
- Phase-based development tracked in task_plan.md
- No comments unless WHY is non-obvious
