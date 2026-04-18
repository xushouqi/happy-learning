from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Textbook, Unit
from app.schemas import TextbookResponse, TextbookWithUnits, UnitResponse

router = APIRouter(prefix="/api/textbooks", tags=["textbooks"])


@router.get("/", response_model=list[TextbookWithUnits])
def list_textbooks(db: Session = Depends(get_db)):
    return db.query(Textbook).all()


@router.get("/{textbook_id}", response_model=TextbookWithUnits)
def get_textbook(textbook_id: int, db: Session = Depends(get_db)):
    textbook = db.query(Textbook).filter(Textbook.id == textbook_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")
    return textbook


# Legacy courses endpoint - redirects to textbooks
courses_router = APIRouter(prefix="/api/courses", tags=["courses"])


@courses_router.get("/", response_model=list[TextbookWithUnits])
def list_courses(db: Session = Depends(get_db)):
    """Legacy endpoint - returns textbooks."""
    return db.query(Textbook).all()


@courses_router.get("/{course_id}", response_model=TextbookWithUnits)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Legacy endpoint - returns a textbook."""
    textbook = db.query(Textbook).filter(Textbook.id == course_id).first()
    if not textbook:
        raise HTTPException(status_code=404, detail="Course not found")
    return textbook


# Units sub-routes
unit_router = APIRouter(prefix="/api/units", tags=["units"])


@unit_router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit
