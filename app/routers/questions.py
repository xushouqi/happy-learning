from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import json, os, random
from app.database import get_db
from app.models import Question, Textbook, Unit
from app.schemas import QuestionResponse, QuestionCreate

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("/by-ids", response_model=list[QuestionResponse])
def get_questions_by_ids(ids: str = Query(...), db: Session = Depends(get_db)):
    """Get questions by comma-separated list of IDs."""
    id_list = [int(x) for x in ids.split(',')]
    return db.query(Question).filter(Question.id.in_(id_list)).all()


@router.get("/word-to-image")
def get_word_to_image():
    """Return mapping of vocabulary words to local image paths."""
    mapping_path = os.path.join("data", "combined_word_to_image.json")
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@router.get("/textbook/{textbook_id}", response_model=list[QuestionResponse])
def list_textbook_questions(textbook_id: int, db: Session = Depends(get_db)):
    """Get all questions for a textbook."""
    return db.query(Question).filter(Question.textbook_id == textbook_id).all()


@router.get("/unit/{unit_id}", response_model=list[QuestionResponse])
def list_questions(unit_id: int, db: Session = Depends(get_db)):
    """Get all questions for a unit."""
    return db.query(Question).filter(Question.unit_id == unit_id).all()


@router.get("/quiz/{unit_id}", response_model=list[QuestionResponse])
def get_quiz_questions(
    unit_id: int,
    per_type: int = Query(10),
    db: Session = Depends(get_db),
):
    """Get N random questions from each available quiz type for a unit."""
    # Dynamically discover which question types exist for this unit
    existing_types = db.query(Question.type).filter(
        Question.unit_id == unit_id
    ).distinct().all()
    existing_types = [t[0] for t in existing_types]

    result = []
    for qtype in existing_types:
        questions = (
            db.query(Question)
            .filter(Question.unit_id == unit_id, Question.type == qtype)
            .all()
        )
        random.shuffle(questions)
        result.extend(questions[:per_type])

    random.shuffle(result)
    return result


@router.get("/random", response_model=list[QuestionResponse])
def random_questions(
    textbook_id: int = Query(None),
    unit_id: int = Query(None),
    question_type: str = Query(None),
    count: int = Query(10),
    db: Session = Depends(get_db),
):
    """Get random questions with optional filters."""
    q = db.query(Question)
    if textbook_id:
        q = q.filter(Question.textbook_id == textbook_id)
    if unit_id:
        q = q.filter(Question.unit_id == unit_id)
    if question_type:
        q = q.filter(Question.type == question_type)
    questions = q.all()
    random.shuffle(questions)
    return questions[:count]


@router.post("/", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
