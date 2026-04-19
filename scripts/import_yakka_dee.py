#!/usr/bin/env python3
"""Import Yakka Dee vocabulary from picture book PDFs.

Renders each PDF page to a PNG image and extracts text per page.
Each episode spans 2-3 pages with ~6-17 word/phrase entries.
Generates 4 question types per episode.
"""
import re
import random
import os
import sys

import fitz  # PyMuPDF

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models import Textbook, Unit, Question

PDF_DIR = "/mnt/f/1.英语启蒙/Yakka Dee开口说单词/Yakka Dee 1-3季单词图卡PDF"
IMAGE_BASE = "yakka_dee/images"
RENDER_DIR = f"data/{IMAGE_BASE}"
os.makedirs(RENDER_DIR, exist_ok=True)
DPI = 150


def extract_episodes(pdf_path: str) -> list[dict]:
    """Extract episodes with rendered page images and text."""
    doc = fitz.open(pdf_path)
    episodes = {}
    current_ep = None
    page_entries = []  # (page_num, text_entries)

    for page_idx, page in enumerate(doc):
        text = page.get_text("text").strip()
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 2 and '宗宗妈' not in l]

        ep_match = re.search(r'S(\d+)E(\d+)', lines[0] if lines else '')
        if ep_match:
            # Save previous episode
            if current_ep and page_entries:
                episodes[current_ep] = page_entries

            current_ep = f"S{ep_match.group(1)}E{ep_match.group(2)}"
            page_entries = []
            lines = lines[1:]  # Remove episode marker

        # Render page to image
        pix = page.get_pixmap(dpi=DPI)
        image_name = f"{current_ep}_p{page_idx:03d}.png"
        image_path = os.path.join(RENDER_DIR, image_name)
        pix.save(image_path)

        page_entries.append({
            "page_num": page_idx,
            "image_url": f"{IMAGE_BASE}/{image_name}",
            "words": lines,
        })

    if current_ep and page_entries:
        episodes[current_ep] = page_entries

    doc.close()
    return episodes


def generate_questions(words: list[str]) -> list[dict]:
    """Generate 4 question types from word/phrase list."""
    word_list = []
    phrase_list = []
    for w in words:
        if (w.endswith(('.', '!', '?')) or
            len(w.split()) >= 3 or
            any(w.lower().startswith(x) for x in [
                "i'm", "i've", "she's", "he's", "it's",
                "we're", "they're", "you're", "let's",
                "don't", "can't"])):
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
        words_in = phrase.split()
        if len(words_in) < 2:
            continue
        questions.append({
            "type": "listen_spell_sentence",
            "answer": " ".join(words_in),
            "options": words_in[:],
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
        image_count = len([f for f in os.listdir(RENDER_DIR) if f.startswith(f"S{season:02d}")])
        print(f"S{season}: {len(episodes)} episodes, {image_count} page images rendered")

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

        sorted_eps = sorted(
            all_episodes.keys(),
            key=lambda x: (
                int(re.search(r'S(\d+)', x).group(1)),
                int(re.search(r'E(\d+)', x).group(1)),
            ),
        )

        for ep_key in sorted_eps:
            unit_num += 1
            page_entries = all_episodes[ep_key]

            # Collect all words for this episode, tracking which page each word is from
            all_words = []
            for entry in page_entries:
                for word in entry["words"]:
                    all_words.append({
                        "word": word,
                        "image_url": entry["image_url"],
                    })

            # Create descriptive unit name from first word
            first_word = all_words[0]["word"].split()[0] if all_words else ep_key
            unit_name = f"{ep_key} - {first_word}"
            unit = Unit(textbook_id=textbook.id, name=unit_name, order=unit_num)
            db.add(unit)
            db.commit()
            db.refresh(unit)

            # Generate questions from just the word texts
            word_texts = [w["word"] for w in all_words]
            questions = generate_questions(word_texts)

            # Build a map of word -> image_url for each question
            word_to_image = {}
            for entry in all_words:
                word_to_image[entry["word"].lower()] = entry["image_url"]

            for i, q in enumerate(questions):
                image_url = word_to_image.get(q["answer"].lower())
                if not image_url:
                    # Fallback: use first page image
                    image_url = page_entries[0]["image_url"] if page_entries else None

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
            print(f"  Unit {unit_num:02d}: {unit_name} -> {len(questions)} questions ({len(all_words)} words, {len(page_entries)} pages)")

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
