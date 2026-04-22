from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models import Score, DailyProgress, UnitProgress, Unit, Textbook, Question
from app.schemas import ScoreCreate, ScoreResponse, DailyProgressCreate, DailyProgressResponse, UnitProgressResponse

router = APIRouter(prefix="/api/scores", tags=["scores"])


@router.post("/", response_model=ScoreResponse)
def record_score(score: ScoreCreate, db: Session = Depends(get_db)):
    db_score = Score(**score.model_dump())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


@router.get("/user/{user_id}", response_model=list[ScoreResponse])
def list_scores(user_id: int, db: Session = Depends(get_db)):
    return db.query(Score).filter(Score.user_id == user_id).all()


@router.post("/unit-complete")
def record_unit_complete(
    user_id: int,
    unit_id: int,
    score: int,
    total: int,
    db: Session = Depends(get_db)
):
    """Record unit quiz completion, update best score, and create daily progress."""
    now = datetime.now(timezone.utc)
    today = now.date()
    unit = db.query(Unit).filter(Unit.id == unit_id).first()

    progress = db.query(UnitProgress).filter(
        UnitProgress.user_id == user_id,
        UnitProgress.unit_id == unit_id
    ).first()

    if progress:
        progress.attempts += 1
        progress.last_attempt = now
        if score > progress.best_score:
            progress.best_score = score
        progress.total_questions = total
        progress.completed = True
    else:
        progress = UnitProgress(
            user_id=user_id,
            unit_id=unit_id,
            best_score=score,
            total_questions=total,
            attempts=1,
            completed=True,
        )
        db.add(progress)

    # Record daily progress
    daily = db.query(DailyProgress).filter(
        DailyProgress.user_id == user_id,
        DailyProgress.unit_id == unit_id,
        DailyProgress.date == today
    ).first()
    if daily:
        if score > daily.total_score:
            daily.total_score = score
        daily.completed = True
    else:
        daily = DailyProgress(
            user_id=user_id,
            unit_id=unit_id,
            date=today,
            total_score=score,
            completed=True,
        )
        db.add(daily)

    db.commit()
    db.refresh(progress)
    return {"success": True, "attempts": progress.attempts, "best_score": progress.best_score}


progress_router = APIRouter(prefix="/api/progress", tags=["progress"])


@progress_router.post("/", response_model=DailyProgressResponse)
def record_progress(progress: DailyProgressCreate, db: Session = Depends(get_db)):
    db_progress = DailyProgress(**progress.model_dump())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress


@progress_router.get("/user/{user_id}", response_model=list[DailyProgressResponse])
def list_progress(user_id: int, db: Session = Depends(get_db)):
    return db.query(DailyProgress).filter(DailyProgress.user_id == user_id).all()


@progress_router.get("/user/{user_id}/calendar")
def get_calendar(user_id: int, year: int, month: int, db: Session = Depends(get_db)):
    """Get daily quiz activity grouped by date for a given month.
    Uses Score table for per-question accuracy, falls back to UnitProgress for historical data."""
    import calendar as cal_mod
    from sqlalchemy import func, cast
    from sqlalchemy import Date as SaDate
    _, days_in_month = cal_mod.monthrange(year, month)
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()

    # Query Score table: aggregate correct/total per unit per day
    score_agg = (
        db.query(
            Score.question_id,
            Score.correct,
            cast(Score.created_at, SaDate).label("attempt_date"),
            Question.unit_id.label("unit_id"),
        )
        .join(Question, Score.question_id == Question.id)
        .filter(Score.user_id == user_id)
        .filter(cast(Score.created_at, SaDate) >= start_date)
        .filter(cast(Score.created_at, SaDate) < end_date)
        .all()
    )

    result = {}
    for question_id, correct, attempt_date, unit_id in score_agg:
        if attempt_date is None:
            continue
        key = attempt_date.isoformat()
        result.setdefault(key, {}).setdefault(unit_id, {
            "correct": 0, "total": 0,
        })
        result[key][unit_id]["total"] += 1
        if correct:
            result[key][unit_id]["correct"] += 1

    # Build final output with unit/textbook info
    unit_cache = {}
    output = {}
    for key, unit_stats in result.items():
        for uid, stats in unit_stats.items():
            if uid not in unit_cache:
                u = db.query(Unit, Textbook.name.label("tb_name"), Textbook.id.label("tb_id")) \
                    .join(Textbook, Unit.textbook_id == Textbook.id) \
                    .filter(Unit.id == uid).first()
                if u:
                    unit_cache[uid] = {
                        "unit_name": u.Unit.name,
                        "textbook_name": u.tb_name,
                        "textbook_id": u.tb_id,
                    }
            info = unit_cache.get(uid)
            if not info:
                continue
            output.setdefault(key, []).append({
                "unit_id": uid,
                "unit_name": info["unit_name"],
                "textbook_name": info["textbook_name"],
                "textbook_id": info["textbook_id"],
                "correct": stats["correct"],
                "total": stats["total"],
                "total_score": 0,
                "total_questions": stats["total"],
                "completed": True,
            })

    # Fallback: UnitProgress for dates with no Score data
    up_records = (
        db.query(UnitProgress, Unit.name.label("unit_name"), Textbook.name.label("textbook_name"), Textbook.id.label("textbook_id"))
        .join(Unit, UnitProgress.unit_id == Unit.id)
        .join(Textbook, Unit.textbook_id == Textbook.id)
        .filter(UnitProgress.user_id == user_id)
        .filter(UnitProgress.last_attempt.isnot(None))
        .all()
    )

    for up, unit_name, textbook_name, textbook_id in up_records:
        if up.last_attempt is None:
            continue
        attempt_date = up.last_attempt.date()
        if attempt_date < start_date or attempt_date >= end_date:
            continue
        key = attempt_date.isoformat()
        existing_units = {e["unit_id"] for e in output.get(key, [])}
        if up.unit_id not in existing_units:
            output.setdefault(key, []).append({
                "unit_id": up.unit_id,
                "unit_name": unit_name,
                "textbook_name": textbook_name,
                "textbook_id": textbook_id,
                "correct": up.best_score,
                "total": up.total_questions,
                "total_score": up.best_score,
                "total_questions": up.total_questions,
                "completed": up.completed,
            })

    return output


@progress_router.get("/user/{user_id}/textbooks", response_model=list[dict])
def get_textbook_progress(user_id: int, db: Session = Depends(get_db)):
    """Get progress summary per textbook with units."""
    textbooks = db.query(Textbook).all()
    all_units = db.query(Unit).order_by(Unit.textbook_id, Unit.order).all()
    all_progress = {
        (p.user_id, p.unit_id): p
        for p in db.query(UnitProgress).filter(UnitProgress.user_id == user_id).all()
    }

    # Group units by textbook
    units_by_textbook = {}
    for u in all_units:
        units_by_textbook.setdefault(u.textbook_id, []).append(u)

    result = []
    for textbook in textbooks:
        units = units_by_textbook.get(textbook.id, [])
        unit_progress_list = []

        tb_best = 0
        tb_total = 0
        tb_units = 0

        for unit in units:
            progress = all_progress.get((user_id, unit.id))

            unit_data = {
                "id": unit.id,
                "name": unit.name,
                "order": unit.order,
                "completed": progress.completed if progress else False,
                "best_score": progress.best_score if progress else 0,
                "total_questions": progress.total_questions if progress else 0,
                "attempts": progress.attempts if progress else 0,
                "last_attempt": progress.last_attempt.isoformat() if progress and progress.last_attempt else None,
            }
            unit_progress_list.append(unit_data)

            if progress and progress.completed:
                tb_best += progress.best_score
                tb_total += progress.total_questions
                tb_units += 1

        result.append({
            "id": textbook.id,
            "name": textbook.name,
            "total_units": len(units),
            "completed_units": tb_units,
            "best_score": tb_best,
            "total_questions": tb_total,
            "units": unit_progress_list,
        })

    return result


@router.delete("/user/{user_id}/unit/{unit_id}")
def clear_unit_progress(user_id: int, unit_id: int, db: Session = Depends(get_db)):
    """Clear all learning progress for a specific unit: scores, unit_progress, daily_progress."""
    # Delete scores for this unit (via question_ids belonging to the unit)
    question_ids = db.query(Question.id).filter(Question.unit_id == unit_id).subquery()
    db.query(Score).filter(
        Score.user_id == user_id,
        Score.question_id.in_(question_ids)
    ).delete(synchronize_session=False)

    # Delete unit_progress
    db.query(UnitProgress).filter(
        UnitProgress.user_id == user_id,
        UnitProgress.unit_id == unit_id
    ).delete(synchronize_session=False)

    # Delete daily_progress
    db.query(DailyProgress).filter(
        DailyProgress.user_id == user_id,
        DailyProgress.unit_id == unit_id
    ).delete(synchronize_session=False)

    db.commit()
    return {"success": True}


@router.get("/user/{user_id}/wrong-questions")
def list_wrong_questions(user_id: int, db: Session = Depends(get_db)):
    """Get questions where the latest attempt was wrong."""
    # Fetch all scores for user, determine latest per question
    all_scores = (
        db.query(Score)
        .filter(Score.user_id == user_id)
        .order_by(Score.question_id, Score.created_at.desc())
        .all()
    )

    latest_per_question = {}
    for s in all_scores:
        if s.question_id not in latest_per_question:
            latest_per_question[s.question_id] = s

    wrong_qids = [s.question_id for s in latest_per_question.values() if not s.correct]
    if not wrong_qids:
        return []

    # Get question details with unit and textbook info
    questions = db.query(
        Question,
        Unit.name.label("unit_name"),
        Textbook.name.label("textbook_name"),
        Textbook.id.label("textbook_id"),
    ).join(Unit, Question.unit_id == Unit.id) \
     .join(Textbook, Unit.textbook_id == Textbook.id) \
     .filter(Question.id.in_(wrong_qids)) \
     .all()

    # Count total wrong attempts per question
    wrong_counts = {}
    for s in all_scores:
        if not s.correct:
            wrong_counts[s.question_id] = wrong_counts.get(s.question_id, 0) + 1

    result = []
    for q, unit_name, textbook_name, textbook_id in questions:
        result.append({
            "id": q.id,
            "type": q.type,
            "options": q.options,
            "answer": q.answer,
            "image_url": q.image_url,
            "audio_text": q.audio_text,
            "sentence": q.sentence,
            "unit_name": unit_name,
            "textbook_name": textbook_name,
            "textbook_id": textbook_id,
            "wrong_count": wrong_counts.get(q.id, 1),
        })
    return result


@router.get("/user/{user_id}/wrong-questions/quiz")
def wrong_questions_quiz(user_id: int, db: Session = Depends(get_db)):
    """Get question IDs for wrong-question quiz mode."""
    all_scores = (
        db.query(Score)
        .filter(Score.user_id == user_id)
        .order_by(Score.question_id, Score.created_at.desc())
        .all()
    )

    latest_per_question = {}
    for s in all_scores:
        if s.question_id not in latest_per_question:
            latest_per_question[s.question_id] = s

    wrong_qids = [s.question_id for s in latest_per_question.values() if not s.correct]
    return {"question_ids": wrong_qids}