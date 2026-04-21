from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routers import users, courses, questions, scores, media, tts

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

# Mount muzzy word card images (must be before / mount)
try:
    app.mount("/muzzy_word_cards", StaticFiles(directory="data/muzzy_word_cards"), name="muzzy_word_cards")
except RuntimeError:
    pass  # muzzy_word_cards directory not present

# Mount Yakka Dee images (must be before / mount)
try:
    app.mount("/yakka_dee", StaticFiles(directory="data/yakka_dee"), name="yakka_dee")
except RuntimeError:
    pass  # yakka_dee directory not present

# Mount static files for production frontend (must be after specific mounts)
try:
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
except RuntimeError:
    pass  # dist not built yet (dev mode)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
