#!/usr/bin/env python3
"""Import Yakka Dee season 2 & 3 vocabulary into the quiz database.

Parses PDF transcripts, extracts English word/phrase entries per topic,
and generates 4 question types:
- image_select_word: 看图选词
- image_select_sentence: 看图选句 (uses full phrase)
- listen_select: 听音选词
- listen_spell_sentence: 听音拼句
"""
import re
import random
import sys
import os

import fitz  # PyMuPDF

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models import Textbook, Unit, Question

PDF_DIR = "/mnt/f/1.英语启蒙/Yakka Dee开口说单词/Yakka Dee 1-3季台词本PDF"


def parse_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF for better font handling."""
    doc = fitz.open(pdf_path)
    all_text = []
    for page in doc:
        all_text.append(page.get_text())
    doc.close()
    return '\n'.join(all_text)


def extract_topics(text: str) -> list[dict]:
    """Extract topic sections and their word entries from PDF text."""
    lines = text.split('\n')
    topics = []
    current_topic = None
    current_words = []

    noise_patterns = [
        "宗宗妈", "What will our yakka be today",
        "Yakka Dee", "Dee! Where are you", "I've seen her",
        "Over there", "SHE LAUGHS", "Dee！", "（ SHE LAUGHS ）",
        "Dee!", "（SHE LAUGHS）", "yakkadee", "Yakka-Dee",
        "公 号", "缺字幕", "目录：", "目录",
    ]

    def is_noise(line):
        return any(p in line for p in noise_patterns)

    for line in lines:
        line = line.strip()
        if not line or is_noise(line):
            continue

        # Topic header: starts with 》
        if line.startswith('》'):
            if current_topic and current_words:
                topics.append({"topic": current_topic, "words": current_words})
            topic_text = line.replace('》', '').strip()
            current_topic = topic_text
            current_words = []
        elif line.startswith('*') and current_topic:
            word = line.lstrip('*').strip()
            # Skip pronunciation guides and long Chinese explanations
            if not word or len(word) > 80:
                continue
            # Remove pronunciation brackets like [ˈstraɪpi]
            word = re.sub(r'\[.*?\]', '', word).strip()
            # Skip lines that are purely Chinese explanations
            if re.match(r'^[\u4e00-\u9fff\[\]\s：、，,.·]+$', word):
                continue
            # Clean trailing Chinese text
            # Keep English part, strip Chinese translation
            english = extract_english(word)
            if english and len(english) > 1:
                current_words.append(english)

    if current_topic and current_words:
        topics.append({"topic": current_topic, "words": current_words})

    return topics


def extract_english(text: str) -> str:
    """Extract the English portion of a word entry."""
    # Remove part-of-speech tags like "n.", "adj.", "adv." (word boundary required)
    text = re.sub(r'\b(?:n|adj|adv|v|prep|pron|phr)\.\s*', '', text)

    # Find the split point between English and Chinese
    result = []
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff' or ch in ['【', '】', '（', '）']:
            break
        result.append(ch)

    english = ''.join(result).strip().rstrip(',.，。')
    # Normalize whitespace
    english = re.sub(r'\s+', ' ', english)
    return english


def generate_questions(topics: list[dict], textbook_id: int, unit_id: int) -> list:
    """Generate 4 question types for all words in topics."""
    # Collect all unique words across topics
    all_words = []
    word_to_topic = {}
    for topic in topics:
        for word in topic["words"]:
            word_lower = word.lower()
            if word_lower not in word_to_topic:
                all_words.append(word)
                word_to_topic[word_lower] = True

    # Separate into single words/phrases vs sentences
    # Phrases: 3+ words, or contain verb/auxiliary words, or end with punctuation
    word_list = []
    phrase_list = []
    for w in all_words:
        words_in_entry = w.split()
        if (w.endswith(('.', '!', '?')) or
            any(w.lower().startswith(x) for x in ["i'm", "i've", "she's", "he's", "it's", "we're", "they're", "you're", "let's", "don't", "can't"]) or
            len(words_in_entry) >= 3):
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
            "image_url": None,  # Will use pollinations.ai fallback
            "audio_text": word,
        })

    # 2. 看图选句 (use longer phrases)
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
            "image_url": None,
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
            "image_url": None,
            "audio_text": word,
        })

    # 4. 听音拼句 (word ordering)
    for phrase in phrase_list:
        words_in_phrase = phrase.split()
        if len(words_in_phrase) < 2:
            continue
        questions.append({
            "type": "listen_spell_sentence",
            "answer": " ".join(words_in_phrase),
            "options": words_in_phrase[:],
            "image_url": None,
            "audio_text": phrase,
        })

    return questions


def main():
    random.seed(42)

    # Parse PDFs
    season_data = {}
    for season, filename in [(2, "yakkadee第二季.pdf"), (3, "yakkadee第三季.pdf")]:
        pdf_path = os.path.join(PDF_DIR, filename)
        if not os.path.exists(pdf_path):
            print(f"SKIP {filename}: not found")
            continue
        text = parse_pdf(pdf_path)
        topics = extract_topics(text)
        season_data[season] = topics
        print(f"Season {season}: {len(topics)} topics")
        for t in topics:
            print(f"  {t['topic']}: {len(t['words'])} words")

    db = SessionLocal()
    try:
        # Delete existing Yakka Dee textbook
        existing = db.query(Textbook).filter(Textbook.name.like("%Yakka%")).first()
        if existing:
            units = db.query(Unit).filter(Unit.textbook_id == existing.id).all()
            for u in units:
                db.query(Question).filter(Question.unit_id == u.id).delete()
            db.query(Unit).filter(Unit.textbook_id == existing.id).delete()
            db.delete(existing)
            db.commit()
            print(f"\nDeleted existing Yakka Dee textbook (id={existing.id})")

        # Create textbook
        textbook = Textbook(name="Yakka Dee 开口说单词", source_path=PDF_DIR)
        db.add(textbook)
        db.commit()
        db.refresh(textbook)
        print(f"Created textbook: {textbook.name} (id={textbook.id})")

        total_questions = 0
        type_counts = {}
        unit_num = 0

        for season in [2, 3]:
            if season not in season_data:
                continue
            topics = season_data[season]

            for topic in topics:
                unit_num += 1
                unit_name = f"S{season} - {topic['topic'].split()[0]}"
                unit = Unit(textbook_id=textbook.id, name=unit_name, order=unit_num)
                db.add(unit)
                db.commit()
                db.refresh(unit)

                questions = generate_questions([topic], textbook.id, unit.id)

                topic_q_count = 0
                for q in questions:
                    question = Question(
                        textbook_id=textbook.id,
                        unit_id=unit.id,
                        type=q["type"],
                        difficulty=1,
                        options=q["options"],
                        answer=q["answer"],
                        image_url=q["image_url"],
                        audio_text=q["audio_text"],
                    )
                    db.add(question)
                    topic_q_count += 1
                    type_counts[q["type"]] = type_counts.get(q["type"], 0) + 1

                db.commit()
                total_questions += topic_q_count
                print(f"  Unit {unit_num:02d}: {unit_name} -> {topic_q_count} questions")

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
