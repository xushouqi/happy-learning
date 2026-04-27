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
    question_types: str = Query(None),
    db: Session = Depends(get_db),
):
    """Get questions for a unit quiz.

    question_types: comma-separated list of types. If None, use all available types.
    For single type selection, returns ALL questions of that type (shuffled).
    For mixed/all types, returns 10 per type (shuffled).
    """
    existing_types = db.query(Question.type).filter(
        Question.unit_id == unit_id
    ).distinct().all()
    existing_types = [t[0] for t in existing_types]

    if question_types:
        requested_types = [t.strip() for t in question_types.split(',') if t.strip()]
        types_to_use = [t for t in requested_types if t in existing_types]
    else:
        types_to_use = existing_types

    result = []
    # 如果只选择了一种题型，返回该题型所有题目
    if len(types_to_use) == 1:
        questions = (
            db.query(Question)
            .filter(Question.unit_id == unit_id, Question.type == types_to_use[0])
            .all()
        )
        random.shuffle(questions)
        result.extend(questions)
    else:
        # 综合题或多题型，每种取10题
        for qtype in types_to_use:
            questions = (
                db.query(Question)
                .filter(Question.unit_id == unit_id, Question.type == qtype)
                .all()
            )
            random.shuffle(questions)
            result.extend(questions[:10])

    random.shuffle(result)
    return result


@router.get("/types/{unit_id}")
def get_available_types(unit_id: int, db: Session = Depends(get_db)):
    """Get available question types for a unit."""
    existing_types = db.query(Question.type).filter(
        Question.unit_id == unit_id
    ).distinct().all()
    return {"types": [t[0] for t in existing_types]}


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


@router.get("/speech-practice/{unit_id}")
def get_speech_practice_questions(
    unit_id: int,
    practice_type: str = Query(...),  # listen_read_sentence or image_read_word
    db: Session = Depends(get_db),
):
    """Get questions for speech practice.

    listen_read_sentence: from image_listen_spell_sentence or listen_spell_sentence questions
    image_read_word: from image_select_word questions
    """
    result = []

    if practice_type == "listen_read_sentence":
        # Get questions from image_listen_spell_sentence or listen_spell_sentence
        questions = (
            db.query(Question)
            .filter(
                Question.unit_id == unit_id,
                Question.type.in_(["image_listen_spell_sentence", "listen_spell_sentence"])
            )
            .all()
        )
        for q in questions:
            result.append({
                "id": q.id,
                "type": "listen_read_sentence",
                "target_text": q.answer,
                "audio_text": q.audio_text,
                "image_url": q.image_url if q.type == "image_listen_spell_sentence" else None,
            })

    elif practice_type == "image_read_word":
        # Get questions from image_select_word
        questions = (
            db.query(Question)
            .filter(Question.unit_id == unit_id, Question.type == "image_select_word")
            .all()
        )
        for q in questions:
            result.append({
                "id": q.id,
                "type": "image_read_word",
                "target_text": q.answer,
                "image_url": q.image_url,
            })

    random.shuffle(result)
    return result


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
