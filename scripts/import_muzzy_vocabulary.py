"""Import Big Muzzy vocabulary images into the happy-learning database as questions."""
import json
import os
import sys
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal, engine, Base
from app.models import Textbook, Unit, Question

VOCAB_PATH = "/home/xsq/.openclaw/workspace/big-muzzy-extract/muzzy_vocabulary.json"
IMAGE_BASE = "muzzy_images"

# Map file prefix to section number
FILE_TO_SECTION = {
    f"{i:02d}_Big Muzzy单词图卡.txt": f"{i:02d}" for i in range(1, 13)
}


def get_image_url(item):
    """Return relative image path or None."""
    image = item.get("image", "")
    if not image:
        return None
    section = FILE_TO_SECTION.get(item["file"])
    if not section:
        return None
    return f"{IMAGE_BASE}/{section}/{image}"


def generate_questions(vocab_items):
    """Generate image_select_word and image_select_sentence questions."""
    word_entries = []  # entries with word + image
    sentence_entries = []  # entries with sentence + image

    for item in vocab_items:
        word = item.get("word", "").strip()
        sentence = item.get("sentence", "").strip()
        image = get_image_url(item)
        if not image:
            continue

        if word:
            word_entries.append({
                "word": word,
                "sentence": sentence,
                "image": image,
                "file": item["file"],
            })
        if sentence:
            sentence_entries.append({
                "word": word,
                "sentence": sentence,
                "image": image,
                "file": item["file"],
            })

    questions = []

    # image_select_word: show image, pick correct word from 4 options
    for entry in word_entries:
        # Collect distractors from same section
        section = entry["file"]
        same_section = [e["word"] for e in word_entries if e["file"] == section and e["word"].lower() != entry["word"].lower()]
        distractors = random.sample(same_section, min(3, len(same_section)))
        if len(distractors) < 3:
            # Fill from other sections
            others = [e["word"] for e in word_entries if e["file"] != section and e["word"].lower() != entry["word"].lower()]
            distractors += random.sample(others, min(3 - len(distractors), len(others)))

        if len(distractors) < 3:
            continue  # Not enough options

        options = [entry["word"]] + distractors
        random.shuffle(options)

        questions.append({
            "type": "image_select_word",
            "answer": entry["word"],
            "options": options,
            "image_url": entry["image"],
            "audio_text": entry["word"],
            "sentence": entry["sentence"] if entry["sentence"] else None,
        })

    # image_select_sentence: show image, pick correct sentence from 4 options
    for entry in sentence_entries:
        section = entry["file"]
        same_section = [e["sentence"] for e in sentence_entries if e["file"] == section and e["sentence"].lower() != entry["sentence"].lower()]
        distractors = random.sample(same_section, min(3, len(same_section)))
        if len(distractors) < 3:
            others = [e["sentence"] for e in sentence_entries if e["file"] != section and e["sentence"].lower() != entry["sentence"].lower()]
            distractors += random.sample(others, min(3 - len(distractors), len(others)))

        if len(distractors) < 3:
            continue

        options = [entry["sentence"]] + distractors
        random.shuffle(options)

        questions.append({
            "type": "image_select_sentence",
            "answer": entry["sentence"],
            "options": options,
            "image_url": entry["image"],
            "audio_text": entry["sentence"],
            "sentence": None,
        })

    return questions


def main():
    random.seed(42)

    with open(VOCAB_PATH) as f:
        vocab = json.load(f)

    print(f"Loaded {len(vocab)} vocabulary entries")

    db = SessionLocal()
    try:
        # Create textbook
        textbook = db.query(Textbook).filter(Textbook.name == "Big Muzzy").first()
        if not textbook:
            textbook = Textbook(name="Big Muzzy", source_path="/home/xsq/.openclaw/workspace/big-muzzy-extract")
            db.add(textbook)
            db.commit()
            db.refresh(textbook)
            print(f"Created textbook: Big Muzzy (id={textbook.id})")
        else:
            print(f"Using existing textbook: Big Muzzy (id={textbook.id})")

        # Create 12 units
        for i in range(1, 13):
            unit = db.query(Unit).filter(
                Unit.textbook_id == textbook.id,
                Unit.name == f"Unit {i:02d}",
            ).first()
            if not unit:
                unit = Unit(textbook_id=textbook.id, name=f"Unit {i:02d}", order=i)
                db.add(unit)
                db.commit()
                db.refresh(unit)
                print(f"  Created unit: Unit {i:02d} (id={unit.id})")
            else:
                print(f"  Using existing unit: Unit {i:02d} (id={unit.id})")

        db.commit()

        # Generate questions
        generated = generate_questions(vocab)
        print(f"\nGenerated {len(generated)} questions total")

        # Count by type
        type_counts = {}
        for q in generated:
            type_counts[q["type"]] = type_counts.get(q["type"], 0) + 1
        for t, c in type_counts.items():
            print(f"  {t}: {c}")

        # Map file to unit
        file_to_unit = {}
        units = db.query(Unit).filter(Unit.textbook_id == textbook.id).all()
        for unit in units:
            num = int(unit.name.split()[-1])
            file_key = f"{num:02d}_Big Muzzy单词图卡.txt"
            file_to_unit[file_key] = unit.id

        # Insert questions
        count = 0
        for q in generated:
            file = None
            for entry in vocab:
                if entry.get("word") == q["answer"] or entry.get("sentence") == q["answer"]:
                    file = entry["file"]
                    break

            unit_id = file_to_unit.get(file)
            if not unit_id:
                continue

            question = Question(
                textbook_id=textbook.id,
                unit_id=unit_id,
                type=q["type"],
                difficulty=1,
                options=q["options"],
                answer=q["answer"],
                image_url=q["image_url"],
                audio_text=q["audio_text"],
                sentence=q["sentence"],
            )
            db.add(question)
            count += 1

        db.commit()
        print(f"\nInserted {count} questions into database!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
