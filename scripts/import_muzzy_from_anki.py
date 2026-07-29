"""Re-import Big Muzzy vocabulary from Anki database with correct image-word mapping."""
import json
import os
import random
import re
import shutil
import sqlite3
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Textbook, Unit, Question

APKG_PATH = "/mnt/f/1.英语启蒙/Big Muzzy 玛泽的故事/07、单词图卡可打印/Big_Muzzy_单词图卡.apkg"
IMAGE_BASE = "/home/xsq/happy-learning/data/muzzy_word_cards"


def extract_anki_media():
    """Extract media files from Anki package with correct section subdirectories."""
    os.makedirs(IMAGE_BASE, exist_ok=True)

    with zipfile.ZipFile(APKG_PATH) as zf:
        media_json = json.loads(zf.read('media').decode('utf-8'))

        for num, filename in media_json.items():
            # Parse section from filename: muzzy_01_img_000.png
            match = re.match(r'muzzy_(\d+)_', filename)
            if not match:
                continue
            section = match.group(1)
            dest_dir = os.path.join(IMAGE_BASE, section)
            os.makedirs(dest_dir, exist_ok=True)

            dest_path = os.path.join(dest_dir, filename)
            if not os.path.exists(dest_path):
                data = zf.read(num)
                with open(dest_path, 'wb') as f:
                    f.write(data)

    print(f"Extracted media to {IMAGE_BASE}")


def parse_anki_notes():
    """Parse Anki notes to get correct word-image-sentence mappings."""
    with zipfile.ZipFile(APKG_PATH) as zf:
        zf.extract('collection.anki2', '/tmp/')

    conn = sqlite3.connect('/tmp/collection.anki2')
    cursor = conn.cursor()
    cursor.execute('SELECT flds FROM notes')

    items = []
    for (flds,) in cursor.fetchall():
        parts = flds.split('\x1f')
        if len(parts) < 4:
            continue

        img_html = parts[0].strip()
        word = parts[1].strip()
        sentence = parts[2].strip().lstrip('\ufeff').strip()
        source = parts[3].strip()

        img_match = re.search(r'src="([^"]+)"', img_html)
        if not img_match:
            continue

        img_file = img_match.group(1)
        section_match = re.match(r'muzzy_(\d+)_', img_file)
        section = section_match.group(1) if section_match else '00'

        items.append({
            'image': img_file,
            'word': word,
            'sentence': sentence,
            'source': source,
            'section': section,
        })

    conn.close()
    os.remove('/tmp/collection.anki2')
    return items


def clean_old_data(db):
    """Remove old Big Muzzy data."""
    textbook = db.query(Textbook).filter(Textbook.name == "Big Muzzy").first()
    if textbook:
        # Delete questions
        db.query(Question).filter(Question.textbook_id == textbook.id).delete()
        # Delete units
        db.query(Unit).filter(Unit.textbook_id == textbook.id).delete()
        # Delete textbook
        db.delete(textbook)
        db.commit()
        print("Cleaned old Big Muzzy data")


def generate_questions(items):
    """Generate questions from parsed items."""
    # Filter to items with words (for image_select_word)
    word_items = [i for i in items if i['word']]
    # Filter to items with sentences (for image_select_sentence)
    sentence_items = [i for i in items if i['sentence']]

    questions = []

    # image_select_word
    for item in word_items:
        section = item['section']
        same_section = [e['word'] for e in word_items
                       if e['section'] == section and e['word'].lower() != item['word'].lower()]
        distractors = random.sample(same_section, min(3, len(same_section)))
        if len(distractors) < 3:
            others = [e['word'] for e in word_items
                     if e['section'] != section and e['word'].lower() != item['word'].lower()]
            distractors += random.sample(others, min(3 - len(distractors), len(others)))

        if len(distractors) < 3:
            continue

        options = [item['word']] + distractors
        random.shuffle(options)

        questions.append({
            'type': 'image_select_word',
            'answer': item['word'],
            'options': options,
            'image_url': f"muzzy_word_cards/{section}/{item['image']}",
            'audio_text': item['word'],
            'sentence': item['sentence'] if item['sentence'] else None,
            'section': section,
        })

    # image_select_sentence
    for item in sentence_items:
        section = item['section']
        same_section = [e['sentence'] for e in sentence_items
                       if e['section'] == section and e['sentence'].lower() != item['sentence'].lower()]
        distractors = random.sample(same_section, min(3, len(same_section)))
        if len(distractors) < 3:
            others = [e['sentence'] for e in sentence_items
                     if e['section'] != section and e['sentence'].lower() != item['sentence'].lower()]
            distractors += random.sample(others, min(3 - len(distractors), len(others)))

        if len(distractors) < 3:
            continue

        options = [item['sentence']] + distractors
        random.shuffle(options)

        questions.append({
            'type': 'image_select_sentence',
            'answer': item['sentence'],
            'options': options,
            'image_url': f"muzzy_word_cards/{section}/{item['image']}",
            'audio_text': item['sentence'],
            'sentence': None,
            'section': section,
        })

    return questions


def main():
    random.seed(42)

    # Step 1: Extract media
    print("Step 1: Extracting Anki media...")
    extract_anki_media()

    # Step 2: Parse notes
    print("Step 2: Parsing Anki notes...")
    items = parse_anki_notes()
    print(f"Parsed {len(items)} items")

    db = SessionLocal()
    try:
        # Step 3: Clean old data
        print("Step 3: Cleaning old data...")
        clean_old_data(db)

        # Step 4: Create new textbook and units
        print("Step 4: Creating textbook and units...")
        textbook = Textbook(name="Big Muzzy", source_path=APKG_PATH)
        db.add(textbook)
        db.flush()
        print(f"  Created textbook: Big Muzzy (id={textbook.id})")

        units = {}
        for i in range(1, 13):
            unit = Unit(textbook_id=textbook.id, name=f"Unit {i:02d}", order=i)
            db.add(unit)
            db.flush()
            units[f"{i:02d}"] = unit.id
            print(f"  Created unit: Unit {i:02d} (id={unit.id})")

        # Step 5: Generate and insert questions
        print("Step 5: Generating questions...")
        questions = generate_questions(items)

        type_counts = {}
        for q in questions:
            type_counts[q['type']] = type_counts.get(q['type'], 0) + 1
        print(f"  Generated {len(questions)} questions:")
        for t, c in type_counts.items():
            print(f"    {t}: {c}")

        count = 0
        for q in questions:
            section = q.pop('section')
            unit_id = units.get(section)
            if not unit_id:
                continue

            question = Question(
                textbook_id=textbook.id,
                unit_id=unit_id,
                type=q['type'],
                difficulty=1,
                options=q['options'],
                answer=q['answer'],
                image_url=q['image_url'],
                audio_text=q['audio_text'],
                sentence=q['sentence'],
            )
            db.add(question)
            count += 1

        db.commit()
        print(f"\nInserted {count} questions!")

        # Verify a sample
        sample = db.query(Question).filter(Question.textbook_id == textbook.id).limit(3).all()
        print("\nSample questions:")
        for q in sample:
            print(f"  type={q.type}, answer={q.answer[:30]}, image={q.image_url}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
