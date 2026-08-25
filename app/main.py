from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import users, courses, questions, scores, media, tts, course_module

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="快乐学英语", description="英语每日一练")

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(courses.courses_router)
app.include_router(courses.unit_router)
app.include_router(questions.router)
app.include_router(scores.router)
app.include_router(scores.progress_router)
app.include_router(media.router)
app.include_router(tts.router)
app.include_router(course_module.router)

# Mount muzzy word card images
try:
    app.mount("/muzzy_word_cards", StaticFiles(directory="data/muzzy_word_cards"), name="muzzy_word_cards")
except RuntimeError:
    pass  # muzzy_word_cards directory not present

# Mount Yakka Dee images
try:
    app.mount("/yakka_dee", StaticFiles(directory="data/yakka_dee"), name="yakka_dee")
except RuntimeError:
    pass  # yakka_dee directory not present

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# SPA fallback: serve static files + index.html for SPA routing
# This replaces StaticFiles mount to support Vue Router history mode
# MUST be registered last — otherwise it shadows all subsequent routes
@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    import os
    dist_dir = "frontend/dist"
    file_path = os.path.join(dist_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(dist_dir, "index.html"))
