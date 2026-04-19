#!/usr/bin/env python3
"""Import New Concept English (新概念英语) from EPUB files.

Book formats:
  - Book 1: Dialogue, vocab with phonetics (odd lessons only, separate files)
  - Book 2: Prose with vocab (2 HTML files, 96 lessons)
  - Book 3: Prose articles (1 HTML file, 60 lessons, no vocab section)
  - Book 4: Prose articles (1 HTML file, 60 lessons, no vocab)

Generates text-only quiz types:
  - listen_select: hear word, choose from options
  - listen_spell: hear word, spell it letter by letter
  - listen_spell_sentence: hear sentence, arrange word tiles
"""
import re
import random
import os
import sys
import zipfile
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models import Textbook, Unit, Question

EPUB_DIR = "/mnt/f/1.英语启蒙/新概念英语动画 电子书（全四册）/电子书/新概念英语 epub格式"


def _parse_book1_lesson(text: str) -> dict | None:
    """Parse a single Book 1 lesson (one HTML file = one lesson)."""
    m = re.match(r'.*?Lesson\s+(\d+)\s+(.+)', text, re.DOTALL)
    if not m:
        return None
    lesson_num = int(m.group(1))
    dialogue = []
    vocab = []
    in_dialogue = False
    in_vocab = False
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("Listen to the tape") or stripped.startswith("First listen"):
            in_dialogue = True
            continue
        if stripped.startswith("听录音"):
            in_dialogue = True
            continue
        if re.match(r"New [Ww]ord", stripped) or "生词" in stripped:
            in_dialogue = False
            in_vocab = True
            continue
        if "参考译文" in stripped:
            break
        if in_dialogue:
            clean = re.sub(r"[^\w\s,?.!-;:()]+", "", stripped).strip()
            if clean and len(clean) > 1:
                dialogue.append(clean)
        elif in_vocab:
            vm = re.match(r'(\S+)\s+\[([^\]]+)\]\s+(.+)', stripped)
            if vm:
                vocab.append({
                    "word": vm.group(1),
                    "phonetic": vm.group(2),
                    "meaning": vm.group(3),
                })
    if dialogue or vocab:
        return {"lesson_num": lesson_num, "dialogue": dialogue, "vocab": vocab}
    return None


def _parse_book2_lesson(block: str) -> dict | None:
    """Parse a Book 2 lesson from a text block."""
    m = re.match(r'Lesson\s+(\d+)\s+(.+)', block)
    if not m:
        return None
    lesson_num = int(m.group(1))
    lines = block.strip().split('\n')
    dialogue = []
    vocab = []
    in_dialogue = False
    in_vocab = False
    in_translation = False
    # Skip: title, Chinese title, listen prompt, question
    skip_count = 4
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if i < skip_count:
            if '?' in stripped:
                skip_count = i + 1
            continue
        if stripped.startswith("Listen to the tape") or stripped.startswith("First listen"):
            in_dialogue = True
            continue
        if stripped.startswith("听录音"):
            in_dialogue = True
            continue
        if re.match(r"New [Ww]ord", stripped) or "生词" in stripped:
            in_dialogue = False
            in_vocab = True
            continue
        if "参考译文" in stripped:
            in_vocab = False
            in_translation = True
            continue
        if re.match(r'^Lesson\s+\d+\s+', stripped):
            break
        if in_dialogue:
            clean = re.sub(r"[^\w\s,?.!-;:()]+", "", stripped).strip()
            if clean and len(clean) > 1:
                dialogue.append(clean)
        elif in_vocab:
            vm = re.match(r'(\S+)\s+\[([^\]]+)\]\s+(.+)', stripped)
            if vm:
                vocab.append({
                    "word": vm.group(1),
                    "phonetic": vm.group(2),
                    "meaning": vm.group(3),
                })
        elif not in_translation:
            clean = re.sub(r"[^\w\s,?.!-;:()]+", "", stripped).strip()
            if clean and len(clean) > 1:
                dialogue.append(clean)
    if dialogue or vocab:
        return {"lesson_num": lesson_num, "dialogue": dialogue, "vocab": vocab}
    return None


def _parse_book3_lesson(block: str) -> dict | None:
    """Parse a Book 3 lesson (prose, no vocab section)."""
    m = re.match(r'Lesson\s+(\d+)\s+(.+)', block)
    if not m:
        return None
    lesson_num = int(m.group(1))
    # Find where actual content starts (after question line)
    lines = block.strip().split('\n')
    content_lines = []
    past_question = False
    for line in lines:
        stripped = line.strip()
        if not past_question:
            if stripped.startswith("Listen to the tape") or stripped.startswith("听录音") or stripped.endswith('?'):
                past_question = True
            continue
        if "参考译文" in stripped:
            break
        if re.match(r'^Lesson\s+\d+\s+', stripped):
            break
        if stripped:
            clean = re.sub(r"[^\w\s,?.!-;:()]+", "", stripped).strip()
            if clean and len(clean) > 1:
                content_lines.append(clean)
    # Split into sentences
    full_text = ' '.join(content_lines)
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s) > 5]
    if sentences:
        return {"lesson_num": lesson_num, "dialogue": sentences, "vocab": []}
    return None


def _parse_book4_lesson(block: str) -> dict | None:
    """Parse a Book 4 lesson (prose, no vocab)."""
    m = re.match(r'Lesson\s*(\d+)\s*\n', block)
    if not m:
        return None
    lesson_num = int(m.group(1))
    body = block[m.end():]
    paragraphs = [p.strip() for p in body.split('\n') if p.strip()]
    full_text = ' '.join(paragraphs)
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s) > 5]
    if sentences:
        return {"lesson_num": lesson_num, "dialogue": sentences, "vocab": []}
    return None


def parse_lessons(epub_path: str, book_num: int) -> list[dict]:
    """Parse lessons from an EPUB file."""
    with zipfile.ZipFile(epub_path) as zf:
        html_files = sorted(
            n for n in zf.namelist()
            if n.startswith("OEBPS/text") and n.endswith(".html")
        )

        # Detect TOC (first file contains many lesson references)
        first_content = zf.read(html_files[0]).decode("utf-8")
        first_soup = BeautifulSoup(first_content, "html.parser")
        first_text = first_soup.get_text()
        toc_lessons = re.findall(r'Lesson\s+(\d+)', first_text)
        has_toc = len(toc_lessons) > 10

        lessons = []

        if book_num == 1:
            # Book 1: each HTML file (after TOC) = one lesson
            files_to_parse = html_files[1:] if has_toc else html_files
            for name in files_to_parse:
                content = zf.read(name).decode("utf-8")
                soup = BeautifulSoup(content, "html.parser")
                text = soup.get_text()
                result = _parse_book1_lesson(text)
                if result:
                    lessons.append(result)

        elif book_num == 2:
            # Book 2: TOC + content L1-80 in first file, L81-96 in second
            # TOC ends when "Lesson 80" is followed by actual lesson content
            files_to_parse = html_files[1:] if has_toc else html_files

            for name in files_to_parse:
                content = zf.read(name).decode("utf-8")
                soup = BeautifulSoup(content, "html.parser")
                text = soup.get_text()
                blocks = re.split(r'(?=Lesson\s+\d+\s+)', text)
                for block in blocks:
                    result = _parse_book2_lesson(block)
                    if result:
                        lessons.append(result)

            # Also parse content from first file if it has TOC (lessons 1-80)
            if has_toc:
                content = zf.read(html_files[0]).decode("utf-8")
                soup = BeautifulSoup(content, "html.parser")
                text = soup.get_text()
                # Find where TOC ends and content begins
                # TOC ends at "Lesson 80 The Crystal Palace" then content starts with "Lesson 1 A private conversation"
                toc_end = text.find("Lesson 80")
                if toc_end > 0:
                    # Content starts after the TOC block ends (look for second "Lesson 1")
                    content_start = text.find("Lesson 1", toc_end + 10)
                    if content_start > 0:
                        content_text = text[content_start:]
                        blocks = re.split(r'(?=Lesson\s+\d+\s+)', content_text)
                        for block in blocks:
                            result = _parse_book2_lesson(block)
                            if result:
                                lessons.append(result)

        elif book_num == 3:
            # Book 3: all lessons in one file, prose style
            content = zf.read(html_files[0]).decode("utf-8")
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text()
            blocks = re.split(r'(?=Lesson\s+\d+\s+)', text)
            for block in blocks:
                result = _parse_book3_lesson(block)
                if result:
                    lessons.append(result)

        elif book_num == 4:
            # Book 4: "LessonN\n" format, prose only
            content = zf.read(html_files[0]).decode("utf-8")
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text()
            blocks = re.split(r'(?=Lesson\s*\d+\s*\n)', text)
            for block in blocks:
                result = _parse_book4_lesson(block)
                if result:
                    lessons.append(result)

    return lessons


def generate_questions(lesson: dict) -> list[dict]:
    """Generate text-only quiz questions from a lesson."""
    questions = []
    vocab_words = [v["word"] for v in lesson["vocab"]]
    sentences = lesson["dialogue"]

    def pick_distractors(word, pool, n):
        others = [x for x in pool if x.lower() != word.lower()]
        return random.sample(others, min(n, len(others)))

    # 1. listen_select: vocabulary words (need 4+ to make options)
    if len(vocab_words) >= 4:
        for word in vocab_words:
            distractors = pick_distractors(word, vocab_words, 3)
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

    # 2. listen_spell: vocabulary words with 3+ letters
    for word in vocab_words:
        clean_word = re.sub(r'[^\w]', '', word)
        if len(clean_word) < 3:
            continue
        questions.append({
            "type": "listen_spell",
            "answer": clean_word,
            "options": list(clean_word),
            "audio_text": word,
        })

    # 3. listen_spell_sentence: sentences with 2+ words
    for line in sentences:
        words = line.split()
        if len(words) < 2 or len(line) < 5:
            continue
        questions.append({
            "type": "listen_spell_sentence",
            "answer": line,
            "options": words[:],
            "audio_text": line,
        })

    return questions


def main():
    random.seed(42)

    db = SessionLocal()
    try:
        # Clear existing New Concept English
        existing = db.query(Textbook).filter(
            Textbook.name.like("%新概念%")
        ).first()
        if existing:
            units = db.query(Unit).filter(Unit.textbook_id == existing.id).all()
            for u in units:
                db.query(Question).filter(Question.unit_id == u.id).delete()
            db.query(Unit).filter(Unit.textbook_id == existing.id).delete()
            db.delete(existing)
            db.commit()
            print(f"Cleared existing New Concept English (id={existing.id})")

        # Create textbook
        textbook = Textbook(
            name="新概念英语",
            source_path=EPUB_DIR,
        )
        db.add(textbook)
        db.commit()
        db.refresh(textbook)
        print(f"Created textbook: {textbook.name} (id={textbook.id})")

        total_questions = 0
        type_counts = {}
        unit_num = 0

        book_names = {1: "第一册", 2: "第二册", 3: "第三册", 4: "第四册"}
        lessons_per_unit_map = {1: 3, 2: 3, 3: 3, 4: 3}

        for book_num in [1, 2, 3, 4]:
            epub_path = os.path.join(
                EPUB_DIR, f"新概念英语{book_names[book_num]}.epub"
            )
            if not os.path.exists(epub_path):
                print(f"SKIP Book {book_num}: not found")
                continue

            lessons = parse_lessons(epub_path, book_num)
            if not lessons:
                print(f"SKIP Book {book_num}: no lessons parsed")
                continue

            lessons.sort(key=lambda l: l["lesson_num"])
            lessons_per_unit = lessons_per_unit_map.get(book_num, 3)

            for i in range(0, len(lessons), lessons_per_unit):
                unit_num += 1
                unit_lessons = lessons[i:i + lessons_per_unit]

                lesson_num = unit_lessons[0]["lesson_num"]
                unit_name = f"Book {book_num} L{lesson_num}"

                unit = Unit(
                    textbook_id=textbook.id,
                    name=unit_name,
                    order=unit_num,
                )
                db.add(unit)
                db.commit()
                db.refresh(unit)

                all_vocab = []
                all_sentences = []
                for lesson in unit_lessons:
                    all_vocab.extend(lesson["vocab"])
                    all_sentences.extend(lesson["dialogue"])

                combined = {
                    "vocab": all_vocab,
                    "dialogue": all_sentences,
                }
                questions = generate_questions(combined)

                for q in questions:
                    question = Question(
                        textbook_id=textbook.id,
                        unit_id=unit.id,
                        type=q["type"],
                        difficulty=1,
                        options=q["options"],
                        answer=q["answer"],
                        image_url=None,
                        audio_text=q["audio_text"],
                    )
                    db.add(question)
                    type_counts[q["type"]] = type_counts.get(q["type"], 0) + 1

                total_questions += len(questions)
                lrange = f"L{unit_lessons[0]['lesson_num']}-{unit_lessons[-1]['lesson_num']}"
                print(
                    f"  Unit {unit_num:02d}: Book{book_num} {lrange} "
                    f"({len(unit_lessons)} lessons) -> {len(questions)} questions "
                    f"({len(all_vocab)} words, {len(all_sentences)} sentences)"
                )

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
