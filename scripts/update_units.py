"""Update database with all Big Muzzy episodes as units, and Didi/Phonics units."""
import sys
sys.path.insert(0, '/home/xsq/happy-learning')
from app.database import SessionLocal
from app.models import Course, Unit, Question, QuestionType

db = SessionLocal()

try:
    # Update Big Muzzy course
    muzzy = db.query(Course).filter(Course.name == "Big Muzzy").first()
    if muzzy:
        muzzy.video_path = "data/videos/big_muzzy_ep01.mp4"

        # Check if we already have 12 units
        existing = db.query(Unit).filter(Unit.course_id == muzzy.id).count()
        if existing < 12:
            # Remove existing 2 units and their questions
            units_to_remove = db.query(Unit).filter(Unit.course_id == muzzy.id).all()
            for u in units_to_remove:
                db.query(Question).filter(Question.unit_id == u.id).delete()
                db.delete(u)
            db.commit()

            # Create 12 units for Big Muzzy
            muzzy_units = [
                {"name": "Episode 1: Hello Muzzy", "order": 1, "script_path": "data/scripts/muzzy_ep1_vocab.txt"},
                {"name": "Episode 2: Muzzy in Love", "order": 2, "script_path": "data/scripts/muzzy_ep2_vocab.txt"},
                {"name": "Episode 3: Muzzy to the Rescue", "order": 3, "script_path": "data/scripts/muzzy_ep3_vocab.txt"},
                {"name": "Episode 4: The Doctor's Visit", "order": 4, "script_path": "data/scripts/muzzy_ep4_vocab.txt"},
                {"name": "Episode 5: Muzzy Saves the Day", "order": 5, "script_path": "data/scripts/muzzy_ep5_vocab.txt"},
                {"name": "Episode 6: Happy Ending", "order": 6, "script_path": "data/scripts/muzzy_ep6_vocab.txt"},
                {"name": "Episode 7: Muzzy Comes Back", "order": 7, "script_path": "data/scripts/muzzy_ep7_vocab.txt"},
                {"name": "Episode 8: Muzzy's Return", "order": 8},
                {"name": "Episode 9: The Big Race", "order": 9, "script_path": "data/scripts/muzzy_ep9_vocab.txt"},
                {"name": "Episode 10: New Adventures", "order": 10},
                {"name": "Episode 11: Muzzy and Friends", "order": 11},
                {"name": "Episode 12: The End", "order": 12, "script_path": "data/scripts/muzzy_ep12_vocab.txt"},
            ]
            for ud in muzzy_units:
                unit = Unit(course_id=muzzy.id, **ud)
                db.add(unit)
            db.commit()

            # Regenerate questions for units that have vocabulary
            from app.services.script_parser import extract_vocabulary
            for unit_name, vocab_file in [
                ("Episode 1: Hello Muzzy", "muzzy_ep1_vocab.txt"),
                ("Episode 2: Muzzy in Love", "muzzy_ep2_vocab.txt"),
                ("Episode 3: Muzzy to the Rescue", "muzzy_ep3_vocab.txt"),
                ("Episode 4: The Doctor's Visit", "muzzy_ep4_vocab.txt"),
                ("Episode 5: Muzzy Saves the Day", "muzzy_ep5_vocab.txt"),
                ("Episode 7: Muzzy Comes Back", "muzzy_ep7_vocab.txt"),
                ("Episode 9: The Big Race", "muzzy_ep9_vocab.txt"),
                ("Episode 12: The End", "muzzy_ep12_vocab.txt"),
            ]:
                import json
                with open("/home/xsq/happy-learning/data/scripts/muzzy_episodes.json") as f:
                    episodes = json.load(f)
                unit = db.query(Unit).filter(Unit.course_id == muzzy.id, Unit.name == unit_name).first()
                if unit:
                    ep_num = int(unit_name.split()[1].rstrip(':'))
                    ep_data = next((e for e in episodes if e["episode"] == ep_num), None)
                    if ep_data:
                        vocab = ep_data["vocab"]
                        # Listen questions
                        for word in vocab[:8]:
                            distractors = [w for w in vocab if w != word]
                            import random; random.seed(ep_num * 100 + vocab.index(word))
                            random.shuffle(distractors)
                            options = [word] + distractors[:3]
                            random.shuffle(options)
                            db.add(Question(unit_id=unit.id, type=QuestionType.LISTEN_SELECT, options=options, answer=word, audio_text=word))
                        # Scramble questions
                        for word in vocab[:5]:
                            if len(word) < 3: continue
                            letters = list(word)
                            random.shuffle(letters)
                            scrambled = ''.join(letters)
                            while scrambled == word: random.shuffle(letters); scrambled = ''.join(letters)
                            db.add(Question(unit_id=unit.id, type=QuestionType.SCRAMBLE_WORD, options=[scrambled], answer=word, audio_text=word))

            db.commit()
            print(f"Big Muzzy: Updated to 12 episodes with questions!")

    # Update Didi's Day
    didi = db.query(Course).filter(Course.name == "Didi's Day").first()
    if didi:
        didi.video_path = "data/videos/didi_ep01.mp4"
        existing = db.query(Unit).filter(Unit.course_id == didi.id).count()
        if existing < 10:
            db.query(Unit).filter(Unit.course_id == didi.id).delete()
            db.commit()
            # Create 10 units (first 10 episodes for kids)
            for i in range(1, 11):
                db.add(Unit(course_id=didi.id, name=f"Episode {i}", order=i,
                           script_path=f"data/videos/didi_ep{i:02d}.mp4"))
            db.commit()
            print(f"Didi's Day: Created 10 episodes!")

    # Update Oxford Phonics
    phonics = db.query(Course).filter(Course.name == "Oxford Phonics").first()
    if phonics:
        phonics.video_path = "data/videos/phonics_a.mp4"
        existing = db.query(Unit).filter(Unit.course_id == phonics.id).count()
        if existing < 26:
            db.query(Unit).filter(Unit.course_id == phonics.id).delete()
            db.commit()
            import string
            for letter in string.ascii_uppercase:
                db.add(Unit(course_id=phonics.id, name=f"Letter {letter}", order=ord(letter)-64,
                           script_path=f"data/videos/phonics_{letter.lower()}.mp4"))
            db.commit()
            print(f"Oxford Phonics: Created 26 letter units!")

    # Summary
    print("\n=== Database Summary ===")
    courses = db.query(Course).all()
    for c in courses:
        units = db.query(Unit).filter(Unit.course_id == c.id).all()
        total_q = sum(db.query(Question).filter(Question.unit_id == u.id).count() for u in units)
        print(f"{c.name}: {len(units)} units, {total_q} questions")

finally:
    db.close()
