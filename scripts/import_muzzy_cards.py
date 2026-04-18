#!/usr/bin/env python3
"""Import Big Muzzy word card JSON into the quiz database.

Generates 4 question types per episode:
- image_select_word: 看图选词
- image_select_sentence: 看图选句
- listen_select_word: 听音选词
- listen_spell_sentence: 听音拼句
"""
import json
import os
import random
import sys
import html as html_mod

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, engine, Base
from app.models import Textbook, Unit, Question, VocabWord

CARDS_PATH = "/home/xsq/happy-learning/data/muzzy_word_cards/word_cards.json"
IMAGE_BASE = "muzzy_word_cards/images"

# Map card file number to episode/unit number
# The doc files 01-12 map to Unit 01-12


def load_cards():
    with open(CARDS_PATH) as f:
        data = json.load(f)
    # Group by file
    by_file = {}
    for card in data["cards"]:
        file_num = card.get("file", "00")
        by_file.setdefault(file_num, []).append(card)
    return by_file


def get_image_path(card):
    """Return the image URL path for the database."""
    img_filename = card["image"].split("/")[-1]
    return f"{IMAGE_BASE}/{img_filename}"


def is_sentence(text):
    text = text.strip()
    if text.endswith((".", "!", "?")):
        return True
    sentence_starts = [
        "i'm", "she's", "he's", "it's", "they're", "we're", "you're",
        "i've", "there's", "don't", "doesn't", "didn't",
        "isn't", "aren't", "wasn't", "won't", "wouldn't", "shouldn't",
        "can't", "couldn't",
    ]
    lower = text.lower()
    if any(lower.startswith(w) for w in sentence_starts):
        return True
    if any(w in lower for w in ["somebody", "nothing", "anything"]):
        return True
    return False


def generate_questions_for_unit(cards):
    """Generate all 4 question types for a unit's cards."""
    # Separate words and sentences, group by image
    # Each card has text + image. One image may have word + sentence cards.
    # Group by image to link word and sentence
    image_map = {}
    for card in cards:
        img = card["image"].split("/")[-1]
        text = html_mod.unescape(card["text"])
        image_map.setdefault(img, []).append(text)

    # Build word list and sentence list with their images
    word_entries = []  # {word, image_url}
    sentence_entries = []  # {sentence, image_url}
    all_words = []
    all_sentences = []

    for img, texts in image_map.items():
        image_url = f"{IMAGE_BASE}/{img}"
        for text in texts:
            if is_sentence(text):
                sentence_entries.append({"sentence": text, "image_url": image_url})
                all_sentences.append(text)
            else:
                word_entries.append({"word": text, "image_url": image_url})
                all_words.append(text)

    questions = []

    # 1. 看图选词: show image, 4 word options
    for entry in word_entries:
        distractors = _pick_distractors(entry["word"], all_words, 3)
        if len(distractors) < 3:
            continue
        options = [entry["word"]] + distractors
        random.shuffle(options)
        questions.append({
            "type": "image_select_word",
            "answer": entry["word"],
            "options": options,
            "image_url": entry["image_url"],
            "audio_text": entry["word"],
        })

    # 2. 看图选句: show image, 4 sentence options
    for entry in sentence_entries:
        distractors = _pick_distractors(entry["sentence"], all_sentences, 3)
        if len(distractors) < 3:
            continue
        options = [entry["sentence"]] + distractors
        random.shuffle(options)
        questions.append({
            "type": "image_select_sentence",
            "answer": entry["sentence"],
            "options": options,
            "image_url": entry["image_url"],
            "audio_text": entry["sentence"],
        })

    # 3. 听音选词: play audio (word), show 4 word options (no image)
    for entry in word_entries:
        distractors = _pick_distractors(entry["word"], all_words, 3)
        if len(distractors) < 3:
            continue
        options = [entry["word"]] + distractors
        random.shuffle(options)
        questions.append({
            "type": "listen_select_word",
            "answer": entry["word"],
            "options": options,
            "image_url": None,
            "audio_text": entry["word"],
        })

    # 4. 听音拼句: play audio (sentence), show word-letter/word buttons to assemble
    # Options are individual words from the sentence (shuffled)
    for entry in sentence_entries:
        sentence = entry["sentence"]
        words = sentence.split()
        if len(words) < 2:
            # Too short for spelling, use word buttons as-is
            options = words[:]
        else:
            options = words[:]
        random.shuffle(options)
        questions.append({
            "type": "listen_spell_sentence",
            "answer": " ".join(words),
            "options": options,
            "image_url": None,
            "audio_text": sentence,
        })

    return questions


def _pick_distractors(correct, pool, count):
    """Pick unique distractors from pool."""
    others = [x for x in pool if x != correct]
    return random.sample(others, min(count, len(others)))


def main():
    random.seed(42)

    by_file = load_cards()
    print(f"Loaded cards for {len(by_file)} files")
    for k in sorted(by_file):
        print(f"  File {k}: {len(by_file[k])} cards")

    db = SessionLocal()
    try:
        # Clear existing Big Muzzy data
        textbook = db.query(Textbook).filter(Textbook.name == "Big Muzzy").first()
        if textbook:
            print(f"\nClearing existing Big Muzzy textbook (id={textbook.id})...")
            # Delete all related data
            units = db.query(Unit).filter(Unit.textbook_id == textbook.id).all()
            for unit in units:
                db.query(Question).filter(Question.unit_id == unit.id).delete()
                db.query(VocabWord).filter(VocabWord.unit_id == unit.id).delete()
            db.query(Unit).filter(Unit.textbook_id == textbook.id).delete()
            db.delete(textbook)
            db.commit()
            print("  Cleared.")
        else:
            print("\nNo existing Big Muzzy textbook found.")

        # Create textbook
        textbook = Textbook(name="Big Muzzy", source_path="data/muzzy_word_cards")
        db.add(textbook)
        db.commit()
        db.refresh(textbook)
        print(f"Created textbook: Big Muzzy (id={textbook.id})")

        # Create 12 units and insert questions
        total_questions = 0
        type_counts = {}

        for i in range(1, 13):
            file_key = f"{i:02d}"
            cards = by_file.get(file_key, [])

            unit = Unit(textbook_id=textbook.id, name=f"Unit {i:02d}", order=i)
            db.add(unit)
            db.commit()
            db.refresh(unit)

            if cards:
                questions = generate_questions_for_unit(cards)
                print(f"\nUnit {i:02d}: {len(cards)} cards -> {len(questions)} questions")

                unit_type_counts = {}
                for q in questions:
                    question = Question(
                        textbook_id=textbook.id,
                        unit_id=unit.id,
                        type=q["type"],
                        difficulty=1,
                        options=q["options"],
                        answer=q["answer"],
                        image_url=q.get("image_url"),
                        audio_text=q.get("audio_text"),
                    )
                    db.add(question)
                    unit_type_counts[q["type"]] = unit_type_counts.get(q["type"], 0) + 1
                    type_counts[q["type"]] = type_counts.get(q["type"], 0) + 1

                for t, c in sorted(unit_type_counts.items()):
                    print(f"  {t}: {c}")
                total_questions += len(questions)
            else:
                print(f"\nUnit {i:02d}: no cards")

        db.commit()
        print(f"\n{'='*50}")
        print(f"Total questions: {total_questions}")
        for t, c in sorted(type_counts.items()):
            print(f"  {t}: {c}")
        print(f"{'='*50}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
