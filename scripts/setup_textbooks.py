"""Create textbooks and units that generate_questions.py expects."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Textbook, Unit

db = SessionLocal()
try:
    # Big Muzzy textbook - 12 units (episodes)
    muzzy = db.query(Textbook).filter(Textbook.name.like("Big Muzzy%")).first()
    if not muzzy:
        muzzy = Textbook(name="Big Muzzy", source_path="data/word_cards")
        db.add(muzzy)
        db.commit()
        db.refresh(muzzy)
        print(f"Created textbook: Big Muzzy (id={muzzy.id})")
    else:
        print(f"Using existing: Big Muzzy (id={muzzy.id})")

    for i in range(1, 13):
        unit = db.query(Unit).filter(Unit.textbook_id == muzzy.id, Unit.order == i).first()
        if not unit:
            level = "L1" if i <= 6 else "L2"
            ep = i if i <= 6 else i - 6
            unit = Unit(textbook_id=muzzy.id, name=f"Episode {ep} ({level})", order=i)
            db.add(unit)
            print(f"  Created Muzzy unit {i}: {unit.name}")
        else:
            print(f"  Exists Muzzy unit {i}: {unit.name}")

    # Oxford Phonics textbook - 5 levels
    phonics = db.query(Textbook).filter(Textbook.name.like("Oxford Phonics%")).first()
    if not phonics:
        phonics = Textbook(name="Oxford Phonics World", source_path="data/phonics")
        db.add(phonics)
        db.commit()
        db.refresh(phonics)
        print(f"\nCreated textbook: Oxford Phonics World (id={phonics.id})")
    else:
        print(f"\nUsing existing: Oxford Phonics (id={phonics.id})")

    phonics_names = {
        1: "Level 1 - Letter Sounds",
        2: "Level 2 - CVC Words",
        3: "Level 3 - Consonant Blends",
        4: "Level 4 - Vowel Teams",
        5: "Level 5 - Complex Patterns",
    }
    for i in range(1, 6):
        unit = db.query(Unit).filter(Unit.textbook_id == phonics.id, Unit.order == i).first()
        if not unit:
            unit = Unit(textbook_id=phonics.id, name=phonics_names[i], order=i)
            db.add(unit)
            print(f"  Created Phonics unit {i}: {unit.name}")
        else:
            print(f"  Exists Phonics unit {i}: {unit.name}")

    db.commit()
    print("\nDone! Textbooks and units ready.")
finally:
    db.close()
