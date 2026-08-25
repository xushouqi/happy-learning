"""课程模块路由。

课程 = 挂在一个教材单元(unit)上的互动授课流程,由多个课时(lesson)组成。
每个课时的 content(JSON)包含有序的互动步骤,步骤类型:
  - story       故事开场(中文引入)
  - learn       学一学:词卡(图 + 词 + 中文 + 例句),前端点击发音
  - listen_tap  听音选图:播放单词发音,从多张图中点选
  - look_choose 看图选词:显示图片,从多个单词中点选
  - sentence    句子跟读:图 + 句子 + 发音,家长/孩子判定跟读

游戏类步骤的具体题目在请求时从 vocab_words 实时组装,配置里只声明单词池。
"""
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Course, CourseLesson, CourseProgress, Textbook, Unit, VocabWord
from app.schemas import CourseResponse, CourseDetailResponse, CourseLessonSummary, CourseProgressCreate

router = APIRouter(prefix="/api/course", tags=["course-module"])


# ---------- helpers ----------

def _img_url(image_path):
    if not image_path:
        return None
    return "/" + image_path if not image_path.startswith("/") else image_path


def _word_pool(words, unit_id, db):
    """返回 {word: {word, image, sentence}} 映射,优先当前单元,找不到再全局兜底。"""
    pool = {}
    if not words:
        return pool
    rows = (
        db.query(VocabWord)
        .filter(VocabWord.word.in_(words))
        .order_by(VocabWord.unit_id == unit_id)
        .all()
    )
    for v in rows:
        pool.setdefault(v.word, {
            "word": v.word,
            "image": _img_url(v.image_path),
            "sentence": v.example_sentence,
        })
    # 兜底:未命中词(如配置里的短语)补空占位
    for w in words:
        pool.setdefault(w, {"word": w, "image": None, "sentence": None})
    return pool


def _sample_targets(words, count):
    targets = list(words)
    random.shuffle(targets)
    return targets[:count]


def _distractors(target, pool, n=3):
    others = [w for w in pool if w != target]
    random.shuffle(others)
    return others[:n]


# ---------- list / detail ----------

def _load_progress(user_id, db):
    """{lesson_id: CourseProgress} 和 {course_id: 课程总星星}。"""
    lesson_progress = {}
    course_stars = {}
    if user_id:
        rows = (
            db.query(CourseProgress)
            .filter(CourseProgress.user_id == user_id)
            .all()
        )
        for p in rows:
            lesson_progress[p.lesson_id] = p
            course_stars[p.course_id] = course_stars.get(p.course_id, 0) + (p.stars or 0)
    return lesson_progress, course_stars


def _course_meta(course, db):
    unit = db.query(Unit).filter(Unit.id == course.unit_id).first()
    textbook = db.query(Textbook).filter(Textbook.id == course.textbook_id).first()
    return {
        "unit_name": unit.name if unit else None,
        "textbook_name": textbook.name if textbook else None,
    }


def _to_summary(lesson, progress):
    p = progress.get(lesson.id)
    return CourseLessonSummary(
        id=lesson.id,
        title=lesson.title,
        subtitle=lesson.subtitle,
        order=lesson.order,
        completed=bool(p and p.completed),
        stars=p.stars if p else 0,
    )


@router.get("/", response_model=list[CourseResponse])
def list_courses(user_id: int = None, db: Session = Depends(get_db)):
    courses = (
        db.query(Course)
        .filter(Course.status == "active")
        .order_by(Course.order, Course.id)
        .all()
    )
    lesson_progress, course_stars = _load_progress(user_id, db)
    result = []
    for c in courses:
        lessons = sorted(c.lessons, key=lambda l: l.order)
        meta = _course_meta(c, db)
        completed = sum(1 for l in lessons if l.id in lesson_progress and lesson_progress[l.id].completed)
        data = CourseResponse(
            id=c.id, textbook_id=c.textbook_id, unit_id=c.unit_id,
            title=c.title, description=c.description, cover_emoji=c.cover_emoji,
            order=c.order, status=c.status,
            lesson_count=len(lessons), completed_lessons=completed,
            total_stars=course_stars.get(c.id, 0),
            **meta,
        )
        result.append(data)
    return result


@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course(course_id: int, user_id: int = None, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson_progress, course_stars = _load_progress(user_id, db)
    lessons = sorted(course.lessons, key=lambda l: l.order)
    meta = _course_meta(course, db)
    completed = sum(1 for l in lessons if l.id in lesson_progress and lesson_progress[l.id].completed)
    return CourseDetailResponse(
        id=course.id, textbook_id=course.textbook_id, unit_id=course.unit_id,
        title=course.title, description=course.description, cover_emoji=course.cover_emoji,
        order=course.order, status=course.status,
        lesson_count=len(lessons), completed_lessons=completed,
        total_stars=course_stars.get(course.id, 0),
        lessons=[_to_summary(l, lesson_progress) for l in lessons],
        **meta,
    )


@router.get("/progress/{user_id}")
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(CourseProgress)
        .filter(CourseProgress.user_id == user_id)
        .order_by(CourseProgress.completed_at.desc())
        .all()
    )
    return [
        {
            "course_id": p.course_id,
            "lesson_id": p.lesson_id,
            "stars": p.stars,
            "completed": p.completed,
            "completed_at": p.completed_at.isoformat() if p.completed_at else None,
        }
        for p in rows
    ]


# ---------- lesson content ----------

@router.get("/{course_id}/lesson/{lesson_id}/content")
def get_lesson_content(course_id: int, lesson_id: int, db: Session = Depends(get_db)):
    lesson = (
        db.query(CourseLesson)
        .filter(CourseLesson.id == lesson_id, CourseLesson.course_id == course_id)
        .first()
    )
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    course = db.query(Course).filter(Course.id == course_id).first()
    unit_id = course.unit_id if course else None

    config_steps = (lesson.content or {}).get("steps", [])
    steps = []

    for step in config_steps:
        stype = step.get("type")
        if stype == "story":
            steps.append({
                "type": "story",
                "title": step.get("title", ""),
                "text": step.get("text", ""),
                "emoji": step.get("emoji", "📖"),
            })
        elif stype == "learn":
            words = step.get("words", [])
            cn_map = step.get("cn", {})
            pool = _word_pool(words, unit_id, db)
            cards = [
                {"word": w, "cn": cn_map.get(w, ""), "image": pool[w]["image"], "sentence": pool[w]["sentence"]}
                for w in words
            ]
            steps.append({"type": "learn", "title": step.get("title", "学一学"), "cards": cards})
        elif stype == "listen_tap":
            words = step.get("words", [])
            pool = _word_pool(words, unit_id, db)
            questions = []
            for target in _sample_targets(words, step.get("count", 4)):
                distract = _distractors(target, pool)
                options = [target] + distract
                random.shuffle(options)
                questions.append({
                    "target": target,
                    "audio": target,
                    "options": [{"word": o, "image": pool[o]["image"]} for o in options],
                })
            steps.append({"type": "listen_tap", "title": step.get("title", "听一听,点一点"), "questions": questions})
        elif stype == "look_choose":
            words = step.get("words", [])
            pool = _word_pool(words, unit_id, db)
            questions = []
            for target in _sample_targets(words, step.get("count", 4)):
                distract = _distractors(target, pool)
                options = [target] + distract
                random.shuffle(options)
                questions.append({
                    "word": target,
                    "image": pool[target]["image"],
                    "options": options,
                })
            steps.append({"type": "look_choose", "title": step.get("title", "看一看,选一选"), "questions": questions})
        elif stype == "sentence":
            sentences = []
            for s in step.get("sentences", []):
                word = s.get("word")
                image = None
                if word:
                    pool = _word_pool([word], unit_id, db)
                    image = pool.get(word, {}).get("image")
                sentences.append({
                    "text": s.get("text", ""),
                    "cn": s.get("cn", ""),
                    "image": image,
                })
            steps.append({"type": "sentence", "title": step.get("title", "句子跟读"), "sentences": sentences})
        else:
            continue

    return {
        "lesson_id": lesson.id,
        "course_id": course_id,
        "title": lesson.title,
        "subtitle": lesson.subtitle,
        "steps": steps,
    }


# ---------- progress recording ----------

@router.post("/lesson-complete")
def complete_lesson(payload: CourseProgressCreate, db: Session = Depends(get_db)):
    lesson = db.query(CourseLesson).filter(CourseLesson.id == payload.lesson_id).first()
    if not lesson or lesson.course_id != payload.course_id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    progress = (
        db.query(CourseProgress)
        .filter(
            CourseProgress.user_id == payload.user_id,
            CourseProgress.lesson_id == payload.lesson_id,
        )
        .first()
    )
    if progress:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        if payload.stars > progress.stars:
            progress.stars = payload.stars
    else:
        progress = CourseProgress(
            user_id=payload.user_id,
            course_id=payload.course_id,
            lesson_id=payload.lesson_id,
            stars=payload.stars,
            completed=True,
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)
    return {"success": True, "stars": progress.stars, "completed": progress.completed}
