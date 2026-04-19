#!/usr/bin/env python3
"""Import Yakka Dee vocabulary from picture book PDFs (word cards).

Extracts vocabulary from S01/S02/S03 picture books (绘本 PDFs).
Each episode has ~6-17 word/phrase entries with images.
Generates 4 question types per episode.
"""
import re
import random
import sys
import os

import fitz  # PyMuPDF

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models import Textbook, Unit, Question

PDF_DIR = "/mnt/f/1.英语启蒙/Yakka Dee开口说单词/Yakka Dee 1-3季单词图卡PDF"

IMAGE_BASE = "yakka_dee/images"
os.makedirs(os.path.join("data", IMAGE_BASE), exist_ok=True)


def extract_episodes(pdf_path: str) -> list[dict]:
    """Extract episodes and their word entries from a picture book PDF."""
    doc = fitz.open(pdf_path)
    episodes = {}
    current_ep = None
    current_words = []
    current_images = []

    for page in doc:
        text = page.get_text("text").strip()
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        # Detect episode marker (S01E01, S02E01, etc.)
        ep_match = re.search(r'S(\d+)E(\d+)', lines[0] if lines else '')
        if ep_match:
            # Save previous episode
            if current_ep and current_words:
                episodes[current_ep] = {
                    "words": current_words,
                    "images": current_images,
                }

            season = ep_match.group(1)
            num = ep_match.group(2)
            current_ep = f"S{season}E{num}"
            current_words = []
            current_images = []
            lines = lines[1:]  # Remove episode marker

        # Extract images
        for img_index, img_info in enumerate(page.get_images()):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            if base_image:
                image_name = f"{current_ep}_{img_index:02d}.{base_image['ext']}"
                image_path = f"data/{IMAGE_BASE}/{image_name}"
                if not os.path.exists(image_path):
                    with open(image_path, "wb") as f:
                        f.write(base_image["image"])
                current_images.append(image_path)

        # Extract text entries
        for line in lines:
            if len(line) > 2 and not line.startswith('公号'):
                current_words.append(line)

    # Save last episode
    if current_ep and current_words:
        episodes[current_ep] = {"words": current_words, "images": current_images}

    doc.close()
    return episodes


def generate_questions(words: list[str]) -> list[dict]:
    """Generate 4 question types from word/phrase list."""
    # Separate words from phrases/sentences
    word_list = []
    phrase_list = []
    for w in words:
        if (w.endswith(('.', '!', '?')) or
            len(w.split()) >= 3 or
            any(w.lower().startswith(x) for x in ["i'm", "i've", "she's", "he's", "it's", "we're", "they're", "you're", "let's", "don't", "can't"])):
            phrase_list.append(w)
        else:
            word_list.append(w)

    questions = []

    def pick_distractors(word, pool, n):
        others = [x for x in pool if x.lower() != word.lower()]
        return random.sample(others, min(n, len(others)))

    # 1. 看图选词
    for word in word_list:
        distractors = pick_distractors(word, word_list, 3)
        if len(distractors) < 3:
            continue
        options = [word] + distractors
        random.shuffle(options)
        questions.append({
            "type": "image_select_word",
            "answer": word,
            "options": options,
            "audio_text": word,
        })

    # 2. 看图选句
    for phrase in phrase_list:
        distractors = pick_distractors(phrase, phrase_list, 3)
        if len(distractors) < 3:
            continue
        options = [phrase] + distractors
        random.shuffle(options)
        questions.append({
            "type": "image_select_sentence",
            "answer": phrase,
            "options": options,
            "audio_text": phrase,
        })

    # 3. 听音选词
    for word in word_list:
        distractors = pick_distractors(word, word_list, 3)
        if len(distractors) < 3:
            continue
        options = [word] + distractors
        random.shuffle(options)
        questions.append({
            "type": "listen_select",
            "answer": word,
            "options": options,
            "audio_text": word,
        })

    # 4. 听音拼句
    for phrase in phrase_list:
        words_in_phrase = phrase.split()
        if len(words_in_phrase) < 2:
            continue
        questions.append({
            "type": "listen_spell_sentence",
            "answer": " ".join(words_in_phrase),
            "options": words_in_phrase[:],
            "audio_text": phrase,
        })

    return questions


def main():
    random.seed(42)

    # Extract from all 3 seasons
    all_episodes = {}
    for season in [1, 2, 3]:
        pdf_path = os.path.join(PDF_DIR, f"Yakka.Dee.S{season:02d} 绘本.pdf")
        if not os.path.exists(pdf_path):
            print(f"SKIP S{season}: {pdf_path} not found")
            continue
        episodes = extract_episodes(pdf_path)
        for ep, data in episodes.items():
            all_episodes[ep] = data
        print(f"S{season}: {len(episodes)} episodes, extracted images to data/{IMAGE_BASE}/")

    db = SessionLocal()
    try:
        # Clear existing Yakka Dee
        existing = db.query(Textbook).filter(Textbook.name.like("%Yakka%")).first()
        if existing:
            units = db.query(Unit).filter(Unit.textbook_id == existing.id).all()
            for u in units:
                db.query(Question).filter(Question.unit_id == u.id).delete()
            db.query(Unit).filter(Unit.textbook_id == existing.id).delete()
            db.delete(existing)
            db.commit()
            print(f"\nCleared existing Yakka Dee (id={existing.id})")

        # Create textbook
        textbook = Textbook(name="Yakka Dee 开口说单词", source_path=PDF_DIR)
        db.add(textbook)
        db.commit()
        db.refresh(textbook)
        print(f"Created textbook: {textbook.name} (id={textbook.id})")

        total_questions = 0
        type_counts = {}
        unit_num = 0

        # Sort episodes by season and episode number
        sorted_eps = sorted(all_episodes.keys(), key=lambda x: (int(re.search(r'S(\d+)', x).group(1)), int(re.search(r'E(\d+)', x).group(1))))

        for ep_key in sorted_eps:
            unit_num += 1
            data = all_episodes[ep_key]
            words = data["words"]
            images = data["images"]

            # Create descriptive unit name from first word (topic name)
            topic_name = words[0].split()[0] if words else ep_key
            unit_name = f"{ep_key} - {topic_name}"
            unit = Unit(textbook_id=textbook.id, name=unit_name, order=unit_num)
            db.add(unit)
            db.commit()
            db.refresh(unit)

            questions = generate_questions(words)

            # Map images to questions (cycle through available images)
            for i, q in enumerate(questions):
                image_url = None
                if images:
                    # Use the image at index matching this question's position
                    img_idx = i % len(images)
                    image_url = f"{IMAGE_BASE}/{os.path.basename(images[img_idx])}"

                question = Question(
                    textbook_id=textbook.id,
                    unit_id=unit.id,
                    type=q["type"],
                    difficulty=1,
                    options=q["options"],
                    answer=q["answer"],
                    image_url=image_url,
                    audio_text=q["audio_text"],
                )
                db.add(question)
                type_counts[q["type"]] = type_counts.get(q["type"], 0) + 1

            total_questions += len(questions)
            print(f"  Unit {unit_num:02d}: {unit_name} -> {len(questions)} questions ({len(images)} images)")

        db.commit()
        print(f"\n{'='*50}")
        print(f"Total units: {unit_num}")
        print(f"Total questions: {total_questions}")
        for t, c in sorted(type_counts.items()):
            print(f"  {t}: {c}")
        print(f"{'='*50}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
