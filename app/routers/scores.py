from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models import Score, DailyProgress, UnitProgress, Unit, Textbook
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
    """Record unit quiz completion, update best score."""
    progress = db.query(UnitProgress).filter(
        UnitProgress.user_id == user_id,
        UnitProgress.unit_id == unit_id
    ).first()

    if progress:
        progress.attempts += 1
        progress.last_attempt = datetime.now(timezone.utc)
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
