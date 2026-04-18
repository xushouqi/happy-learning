"""Seed initial data: create courses with units and questions."""
from app.database import SessionLocal, engine, Base
from app.models import Course, Unit, Question, QuestionType, User
import random, string

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    # Create users
    if db.query(User).count() == 0:
        db.add_all([
            User(name="姐姐", avatar="🐰"),
            User(name="妹妹", avatar="🐱"),
        ])
        db.commit()

    # Courses and units already created by setup_db.py
    if db.query(Course).count() == 0:
        print("No courses found. Run setup_db.py first.")
    else:
        courses = db.query(Course).all()
        muzzy = courses[0]  # Big Muzzy
        didi = courses[1]   # Didi's Day
        phonics = courses[2] # Oxford Phonics

        # Vocabulary per unit type
        muzzy_vocab = {
            1: ['hello', 'muzzy', 'king', 'queen', 'princess', 'bob', 'garden', 'castle'],
            2: ['love', 'beautiful', 'flower', 'ring', 'marry', 'happy', 'wedding', 'forever'],
            3: ['help', 'rescue', 'save', 'brave', 'danger', 'run', 'escape', 'safe'],
            4: ['doctor', 'sick', 'hospital', 'medicine', 'headache', 'pain', 'better', 'well'],
            5: ['hero', 'strong', 'powerful', 'protect', 'guard', 'brave', 'save', 'day'],
            6: ['happy', 'ending', 'wedding', 'love', 'beautiful', 'forever', 'king', 'queen'],
            7: ['come', 'back', 'return', 'miss', 'friend', 'happy', 'surprise', 'welcome'],
            8: ['magic', 'robot', 'computer', 'garden', 'surprise', 'friend', 'help', 'return'],
            9: ['race', 'fast', 'slow', 'win', 'run', 'car', 'boat', 'plane'],
            10: ['new', 'adventure', 'travel', 'fast', 'slow', 'stop', 'go', 'journey'],
            11: ['friend', 'together', 'play', 'fun', 'game', 'sing', 'dance', 'party'],
            12: ['end', 'goodbye', 'farewell', 'thank', 'love', 'happy', 'forever', 'bye'],
        }

        didi_vocab = {
            1: ['hello', 'friend', 'play', 'happy', 'good', 'nice', 'day', 'sun'],
            2: ['color', 'red', 'blue', 'green', 'yellow', 'pink', 'white', 'black'],
            3: ['cat', 'dog', 'bird', 'fish', 'rabbit', 'duck', 'hen', 'cow'],
            4: ['eat', 'drink', 'apple', 'banana', 'cake', 'rice', 'bread', 'milk'],
            5: ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'],
            6: ['big', 'small', 'tall', 'short', 'long', 'round', 'thin', 'fat'],
            7: ['up', 'down', 'in', 'out', 'on', 'under', 'over', 'behind'],
            8: ['run', 'jump', 'walk', 'sit', 'stand', 'climb', 'fly', 'swim'],
            9: ['morning', 'afternoon', 'evening', 'night', 'today', 'tomorrow', 'yesterday', 'noon'],
            10: ['family', 'mother', 'father', 'sister', 'brother', 'baby', 'home', 'house'],
            11: ['water', 'fire', 'earth', 'wind', 'rain', 'snow', 'sun', 'moon'],
            12: ['head', 'eyes', 'nose', 'mouth', 'ears', 'hands', 'feet', 'hair'],
            13: ['happy', 'sad', 'angry', 'scared', 'tired', 'hungry', 'thirsty', 'sick'],
            14: ['shirt', 'pants', 'shoes', 'hat', 'dress', 'coat', 'socks', 'jacket'],
            15: ['bed', 'table', 'chair', 'door', 'window', 'room', 'house', 'garden'],
            16: ['car', 'bus', 'train', 'plane', 'boat', 'bike', 'truck', 'taxi'],
            17: ['tree', 'flower', 'grass', 'leaf', 'root', 'stem', 'fruit', 'seed'],
            18: ['cook', 'bake', 'wash', 'clean', 'sweep', 'mop', 'tidy', 'organize'],
            19: ['read', 'write', 'draw', 'paint', 'color', 'cut', 'glue', 'paste'],
            20: ['spring', 'summer', 'autumn', 'winter', 'warm', 'hot', 'cool', 'cold'],
            21: ['lion', 'tiger', 'bear', 'monkey', 'elephant', 'giraffe', 'zebra', 'panda'],
            22: ['chicken', 'sheep', 'pig', 'horse', 'goat', 'duck', 'goose', 'turkey'],
            23: ['nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen'],
            24: ['wide', 'narrow', 'deep', 'shallow', 'heavy', 'light', 'hard', 'soft'],
            25: ['front', 'back', 'left', 'right', 'next', 'near', 'far', 'between'],
            26: ['dance', 'sing', 'laugh', 'cry', 'smile', 'frown', 'shout', 'whisper'],
            27: ['sleep', 'wake', 'dream', 'rest', 'nap', 'bedtime', 'midnight', 'dawn'],
            28: ['grandma', 'grandpa', 'uncle', 'aunt', 'cousin', 'nephew', 'niece', 'family'],
            29: ['please', 'sorry', 'excuse', 'welcome', 'cheers', 'goodbye', 'hello', 'thanks'],
            30: ['always', 'never', 'sometimes', 'often', 'usually', 'rarely', 'every', 'each'],
        }

        phonics_vocab = {}
        for i, letter in enumerate('abcdefghijklmnopqrstuvwxyz'):
            uid = 43 + i
            phonics_vocab[uid] = [
                letter.upper(), letter.lower(), f'{letter} is for', f'big {letter}',
                f'small {letter}', f'apple {letter}', f'{letter} says', f'letter {letter}',
            ]

        random.seed(42)

        def generate_questions(unit_id, vocab, phrases=None):
            questions = []
            phrases = phrases or vocab[:4]

            # Listen select questions
            for word in vocab[:6]:
                distractors = [w for w in vocab if w != word]
                random.shuffle(distractors)
                options = [word] + distractors[:3]
                random.shuffle(options)
                questions.append({
                    'unit_id': unit_id, 'type': QuestionType.LISTEN_SELECT,
                    'options': options, 'answer': word, 'audio_text': word,
                })

            # Image select word questions
            for phrase in phrases[:3]:
                words = [w for w in phrase.split() if len(w) > 2 and w.lower() not in ('the', 'and', 'for', 'you', 'are', 'can', 'has', 'was', 'how', 'let', 'say', 'big', 'see')]
                if not words:
                    words = [w for w in phrase.split() if len(w) > 2]
                if not words:
                    continue
                key_word = random.choice(words).strip(".,!'\"?").lower()
                distractors = [w for w in vocab if w.lower() != key_word]
                random.shuffle(distractors)
                options = [key_word] + distractors[:3]
                random.shuffle(options)
                questions.append({
                    'unit_id': unit_id, 'type': QuestionType.IMAGE_SELECT_WORD,
                    'options': options, 'answer': key_word,
                })

            # Scramble word questions
            for word in vocab[:3]:
                if len(word) < 3:
                    continue
                letters = list(word)
                scrambled = ''.join(letters)
                attempts = 0
                while scrambled == word and attempts < 10:
                    random.shuffle(letters)
                    scrambled = ''.join(letters)
                    attempts += 1
                if scrambled == word:
                    continue
                questions.append({
                    'unit_id': unit_id, 'type': QuestionType.SCRAMBLE_WORD,
                    'options': [scrambled], 'answer': word, 'audio_text': word,
                })

            return questions

        total = 0
        # Big Muzzy questions (units 1-12)
        for uid, vocab in muzzy_vocab.items():
            phrases = [f'I see {vocab[0]}', f'The {vocab[1]} is here', f'My {vocab[2]}']
            qs = generate_questions(uid, vocab, phrases)
            for q in qs:
                db.add(Question(**q))
            total += len(qs)
            print(f'  Muzzy Unit {uid}: {len(qs)} questions')

        # Didi questions (units 13-42)
        for uid, vocab in didi_vocab.items():
            phrases = [f'I see {vocab[0]}', f'The {vocab[1]} is here', f'My {vocab[2]}']
            qs = generate_questions(uid, vocab, phrases)
            for q in qs:
                db.add(Question(**q))
            total += len(qs)
            print(f'  Didi Unit {uid}: {len(qs)} questions')

        # Phonics questions (units 43-68)
        for uid, vocab in phonics_vocab.items():
            letter = chr(uid - 43 + ord('a'))
            phrases = [f'{letter} is for apple', f'Say {letter}', f'Big {letter}']
            qs = generate_questions(uid, vocab, phrases)
            for q in qs:
                db.add(Question(**q))
            total += len(qs)
            print(f'  Phonics Unit {uid}: {len(qs)} questions')

        db.commit()
        print(f'\nTotal: {total} questions created')

finally:
    db.close()
