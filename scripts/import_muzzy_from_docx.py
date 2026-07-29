"""Import Big Muzzy vocabulary from .docx files with correct image-word mapping.

The .docx files were converted from the original .doc files via Word COM SaveAs2(format=12).
Images in .docx word/media/ are in document order, and document.xml text gives the
correct word-sentence pairs. This replaces the Anki-based import which had images
in binary storage order (wrong).
"""
import os
import random
import re
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Textbook, Unit, Question, VocabWord

DOCX_DIR = "/mnt/c/temp/muzzy_docx"
IMAGE_SRC_DIR = "/tmp/muzzy_final_images"
IMAGE_DST_BASE = "/home/xsq/happy-learning/data/muzzy_word_cards"


def parse_docx_unit(unit_str):
    """Parse a .docx file to extract word-image-sentence entries in document order."""
    docx_path = os.path.join(DOCX_DIR, f"unit{unit_str}.docx")
    if not os.path.exists(docx_path):
        print(f"  WARNING: {docx_path} not found")
        return []

    with zipfile.ZipFile(docx_path) as zf:
        doc_xml = zf.read('word/document.xml').decode('utf-8')
        rels_xml = zf.read('word/_rels/document.xml.rels').decode('utf-8')

    rid_to_image = {}
    for m in re.finditer(r'Id="(rId\d+)"[^>]*Target="(media/[^"]*)"', rels_xml):
        rid_to_image[m.group(1)] = os.path.basename(m.group(2))

    paragraphs = re.findall(r'<w:p[^>]*>(.*?)</w:p>', doc_xml, re.DOTALL)

    entries = []
    current = {'images': [], 'texts': []}
    for p in paragraphs:
        texts = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', p)
        text = ''.join(texts).strip()
        rids = re.findall(r'r:(?:embed|id)="(rId\d+)"', p)
        images = [rid_to_image[r] for r in rids if r in rid_to_image]

        if images:
            if current['texts'] or current['images']:
                entries.append(current)
            current = {'images': images, 'texts': []}
        if text:
            current['texts'].append(text)

    if current['texts'] or current['images']:
        entries.append(current)

    results = []
    for entry in entries:
        if not entry['images']:
            continue

        word = entry['texts'][0] if entry['texts'] else ''
        sentence = entry['texts'][1] if len(entry['texts']) > 1 else ''

        word = word.strip().rstrip('/')
        if not word:
            continue

        # Skip template/scaffold entries
        if '___' in word or '___' in sentence:
            continue
        if re.match(r'^(Name|Age|Date)\s*[:：]', word + ' ' + sentence):
            continue

        results.append({
            'word': word,
            'sentence': sentence,
            'src_image': entry['images'][0],
            'section': unit_str,
        })

    return results


def copy_images(entries, unit_str):
    """Copy .docx images to data directory with sequential naming."""
    src_dir = os.path.join(IMAGE_SRC_DIR, unit_str)
    dst_dir = os.path.join(IMAGE_DST_BASE, unit_str)
    os.makedirs(dst_dir, exist_ok=True)

    for i, entry in enumerate(entries):
        src_file = os.path.join(src_dir, entry['src_image'])
        if not os.path.exists(src_file):
            print(f"  WARNING: source image not found: {src_file}")
            entry['image'] = None
            continue

        ext = os.path.splitext(entry['src_image'])[1].lower()
        if ext == '.jpeg':
            ext = '.jpg'
        new_name = f"muzzy_{unit_str}_img_{i:03d}{ext}"
        dst_file = os.path.join(dst_dir, new_name)

        shutil.copy2(src_file, dst_file)
        entry['image'] = new_name

    return entries


def clean_old_muzzy(db):
    """Remove old Big Muzzy data."""
    textbook = db.query(Textbook).filter(Textbook.name == "Big Muzzy").first()
    if textbook:
        units = db.query(Unit).filter(Unit.textbook_id == textbook.id).all()
        for unit in units:
            db.query(Question).filter(Question.unit_id == unit.id).delete()
            db.query(VocabWord).filter(VocabWord.unit_id == unit.id).delete()
        db.query(Unit).filter(Unit.textbook_id == textbook.id).delete()
        db.delete(textbook)
        db.commit()
        print("  Cleaned old Big Muzzy data")


def normalize_word(word):
    """Normalize word for matching: lowercase, strip articles."""
    w = word.lower().strip()
    w = re.sub(r'^(an?|some|the)\s+', '', w)
    w = w.rstrip('.')
    return w


def generate_questions(all_items):
    """Generate questions from parsed items."""
    word_items = [i for i in all_items if i['word'] and i.get('image')]
    sentence_items = [i for i in word_items
                      if i['sentence']
                      and normalize_word(i['sentence']) != normalize_word(i['word'])
                      and len(i['sentence'].split()) >= 2]

    questions = []

    # image_select_word
    for item in word_items:
        section = item['section']
        same_section = [e['word'] for e in word_items
                        if e['section'] == section
                        and normalize_word(e['word']) != normalize_word(item['word'])]
        distractors = random.sample(same_section, min(3, len(same_section)))
        if len(distractors) < 3:
            others = [e['word'] for e in word_items
                      if e['section'] != section
                      and normalize_word(e['word']) != normalize_word(item['word'])]
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
            'sentence': item['sentence'] or None,
            'section': section,
        })

    # image_select_sentence
    for item in sentence_items:
        section = item['section']
        same_section = [e['sentence'] for e in sentence_items
                        if e['section'] == section and e['sentence'] != item['sentence']]
        distractors = random.sample(same_section, min(3, len(same_section)))
        if len(distractors) < 3:
            others = [e['sentence'] for e in sentence_items
                      if e['section'] != section and e['sentence'] != item['sentence']]
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

    # listen_select
    for item in word_items:
        section = item['section']
        same_section = [e['word'] for e in word_items
                        if e['section'] == section
                        and normalize_word(e['word']) != normalize_word(item['word'])]
        distractors = random.sample(same_section, min(3, len(same_section)))
        if len(distractors) < 3:
            others = [e['word'] for e in word_items
                      if e['section'] != section
                      and normalize_word(e['word']) != normalize_word(item['word'])]
            distractors += random.sample(others, min(3 - len(distractors), len(others)))
        if len(distractors) < 3:
            continue

        options = [item['word']] + distractors
        random.shuffle(options)
        questions.append({
            'type': 'listen_select',
            'answer': item['word'],
            'options': options,
            'image_url': None,
            'audio_text': item['word'],
            'sentence': item['sentence'] or None,
            'section': section,
        })

    # listen_spell
    for item in word_items:
        if len(item['word']) < 3:
            continue
        section = item['section']
        questions.append({
            'type': 'listen_spell',
            'answer': item['word'],
            'options': [item['word']],
            'image_url': None,
            'audio_text': item['word'],
            'sentence': item['sentence'] or None,
            'section': section,
        })

    # listen_spell_sentence
    for item in sentence_items:
        sentence = item['sentence']
        words = sentence.split()
        if len(words) < 2:
            continue
        section = item['section']
        other_words = []
        for s in [e['sentence'] for e in sentence_items
                  if e['section'] == section and e['sentence'] != sentence]:
            for w in s.split():
                if w not in words and w not in other_words:
                    other_words.append(w)
        if not other_words:
            other_words = [e['word'] for e in word_items
                           if e['section'] == section and e['word'] not in words]
        random.shuffle(other_words)
        distractor = other_words[:1] if other_words else []
        options = words + distractor
        random.shuffle(options)
        questions.append({
            'type': 'listen_spell_sentence',
            'answer': sentence,
            'options': options,
            'image_url': None,
            'audio_text': sentence,
            'sentence': sentence,
            'section': section,
        })

    # image_listen_spell_sentence
    for item in sentence_items:
        sentence = item['sentence']
        words = sentence.split()
        if len(words) < 2:
            continue
        section = item['section']
        other_words = []
        for s in [e['sentence'] for e in sentence_items
                  if e['section'] == section and e['sentence'] != sentence]:
            for w in s.split():
                if w not in words and w not in other_words:
                    other_words.append(w)
        if not other_words:
            other_words = [e['word'] for e in word_items
                           if e['section'] == section and e['word'] not in words]
        random.shuffle(other_words)
        distractor = other_words[:1] if other_words else []
        options = words + distractor
        random.shuffle(options)
        questions.append({
            'type': 'image_listen_spell_sentence',
            'answer': sentence,
            'options': options,
            'image_url': f"muzzy_word_cards/{section}/{item['image']}",
            'audio_text': sentence,
            'sentence': sentence,
            'section': section,
        })

    return questions


def main():
    random.seed(42)

    print("=" * 60)
    print("Big Muzzy Import from .docx (correct image-word mapping)")
    print("=" * 60)

    # Step 1: Parse all units from .docx
    print("\nStep 1: Parsing .docx files...")
    all_items = []
    for unit in range(1, 13):
        unit_str = f"{unit:02d}"
        entries = parse_docx_unit(unit_str)
        print(f"  Unit {unit_str}: {len(entries)} word entries")
        all_items.extend(entries)
    print(f"  Total: {len(all_items)} entries")

    # Step 2: Copy images with correct naming
    print("\nStep 2: Copying images with correct names...")
    for unit in range(1, 13):
        unit_str = f"{unit:02d}"
        unit_items = [i for i in all_items if i['section'] == unit_str]
        copy_images(unit_items, unit_str)
        valid = sum(1 for i in unit_items if i.get('image'))
        print(f"  Unit {unit_str}: {valid}/{len(unit_items)} images copied")

    # Step 3: Clean and rebuild database
    db = SessionLocal()
    try:
        print("\nStep 3: Cleaning old data...")
        clean_old_muzzy(db)

        print("\nStep 4: Creating textbook and units...")
        textbook = Textbook(name="Big Muzzy", source_path="data/muzzy_word_cards")
        db.add(textbook)
        db.flush()
        print(f"  Created textbook: Big Muzzy (id={textbook.id})")

        units = {}
        for i in range(1, 13):
            unit = Unit(textbook_id=textbook.id, name=f"Unit {i:02d}", order=i)
            db.add(unit)
            db.flush()
            units[f"{i:02d}"] = unit.id

        # Step 5: Generate questions
        print("\nStep 5: Generating questions...")
        questions = generate_questions(all_items)

        type_counts = {}
        for q in questions:
            type_counts[q['type']] = type_counts.get(q['type'], 0) + 1
        print(f"  Generated {len(questions)} questions:")
        for t, c in sorted(type_counts.items()):
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
        print(f"\n  Inserted {count} questions!")

        # Step 6: Insert vocab words
        print("\nStep 6: Inserting vocab words...")
        word_items = [i for i in all_items if i['word'] and i.get('image')]
        vocab_count = 0
        for item in word_items:
            section = item['section']
            unit_id = units.get(section)
            if not unit_id:
                continue
            db.add(VocabWord(
                textbook_id=textbook.id,
                unit_id=unit_id,
                word=item['word'],
                image_path=f"muzzy_word_cards/{section}/{item['image']}",
                example_sentence=item['sentence'] or None,
            ))
            vocab_count += 1
        db.commit()
        print(f"  Inserted {vocab_count} vocab words")

        # Verify samples
        print("\n=== Verification samples ===")
        for unit_num in [1, 4, 7]:
            us = f"{unit_num:02d}"
            unit_id = units[us]
            sample = db.query(Question).filter(
                Question.unit_id == unit_id,
                Question.type == 'image_listen_spell_sentence'
            ).limit(3).all()
            print(f"\n  Unit {us} image_listen_spell_sentence:")
            for q in sample:
                print(f"    img={q.image_url} | answer={q.answer[:50]}")

    finally:
        db.close()

    print("\n" + "=" * 60)
    print("Done! Images are now correctly mapped from .docx source.")
    print("=" * 60)


if __name__ == "__main__":
    main()
