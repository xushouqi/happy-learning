"""Generate questions for all units that currently have no questions."""
import sys, random
sys.path.insert(0, '/home/xsq/happy-learning')
from app.database import SessionLocal
from app.models import Question, QuestionType

# Vocabulary per unit (manually curated for missing episodes + courses)
UNIT_VOCAB = {
    # --- Big Muzzy missing episodes ---
    12: {  # Episode 6: Happy Ending
        'vocab': ['happy', 'ending', 'wedding', 'love', 'beautiful', 'king', 'queen', 'princess', 'castle', 'forever'],
        'phrases': ['Happy ending', 'I love you', 'Good night', 'Here you are'],
    },
    14: {  # Episode 8: Muzzy's Return
        'vocab': ['back', 'return', 'friend', 'help', 'magic', 'surprise', 'happy', 'garden', 'robot', 'computer'],
        'phrases': ['I\'m back', 'Good morning', 'Can I help', 'How do you do'],
    },
    16: {  # Episode 10: New Adventures
        'vocab': ['new', 'adventure', 'travel', 'car', 'train', 'boat', 'plane', 'fast', 'slow', 'stop'],
        'phrases': ['Let\'s go', 'Good bye', 'Come here', 'Look at this'],
    },
    17: {  # Episode 11: Muzzy and Friends
        'vocab': ['friend', 'together', 'play', 'fun', 'game', 'sing', 'dance', 'music', 'party', 'laugh'],
        'phrases': ['Let\'s play', 'Good evening', 'Thank you', 'How are you'],
    },
    # --- Didi's Day (basic children vocab) ---
    19: {'vocab': ['hello', 'friend', 'play', 'fun', 'happy', 'good', 'nice', 'day', 'sun', 'smile'], 'phrases': ['Hello friend', 'Good day', 'Let\'s play', 'I am happy']},
    20: {'vocab': ['color', 'red', 'blue', 'green', 'yellow', 'pink', 'white', 'black', 'orange', 'purple'], 'phrases': ['I like red', 'What color', 'Blue sky', 'Green grass']},
    21: {'vocab': ['cat', 'dog', 'bird', 'fish', 'rabbit', 'duck', 'hen', 'cow', 'pig', 'horse'], 'phrases': ['I see a cat', 'The dog runs', 'Little bird', 'Fish swim']},
    22: {'vocab': ['eat', 'drink', 'apple', 'banana', 'cake', 'rice', 'bread', 'milk', 'water', 'juice'], 'phrases': ['I eat apple', 'Drink milk', 'I like cake', 'Yummy bread']},
    23: {'vocab': ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'], 'phrases': ['Count to ten', 'One two three', 'I see five', 'How many']},
    24: {'vocab': ['big', 'small', 'tall', 'short', 'long', 'round', 'thin', 'fat', 'wide', 'narrow'], 'phrases': ['Big tree', 'Small cat', 'How tall', 'A long day']},
    25: {'vocab': ['up', 'down', 'in', 'out', 'on', 'under', 'over', 'behind', 'front', 'next'], 'phrases': ['Up and down', 'In the box', 'Under the table', 'On top']},
    26: {'vocab': ['run', 'jump', 'walk', 'sit', 'stand', 'climb', 'fly', 'swim', 'dance', 'sing'], 'phrases': ['Run fast', 'Jump high', 'Let\'s dance', 'I can swim']},
    27: {'vocab': ['morning', 'afternoon', 'evening', 'night', 'today', 'tomorrow', 'yesterday', 'noon', 'bed', 'wake'], 'phrases': ['Good morning', 'Good night', 'Wake up', 'Time to sleep']},
    28: {'vocab': ['family', 'mother', 'father', 'sister', 'brother', 'baby', 'grandma', 'grandpa', 'home', 'house'], 'phrases': ['I love family', 'My home', 'Good bye', 'See you']},
    # --- Oxford Phonics (letter-based) ---
}

for i, letter in enumerate('abcdefghijklmnopqrstuvwxyz'):
    uid = 29 + i
    UNIT_VOCAB[uid] = {
        'vocab': [letter.upper(), letter.lower(), f'{letter} is for', f'big {letter}', f'small {letter}', f'apple {letter}', f'{letter} says', f'letter {letter}'],
        'phrases': [f'{letter} is for apple', f'Say {letter}', f'Big {letter}', f'Small {letter}'],
    }


def generate_listen_questions(vocab, unit_id):
    questions = []
    for word in vocab[:8]:
        distractors = [w for w in vocab if w != word]
        random.shuffle(distractors)
        options = [word] + distractors[:3]
        random.shuffle(options)
        questions.append({
            'unit_id': unit_id, 'type': QuestionType.LISTEN_SELECT,
            'options': options, 'answer': word, 'audio_text': word,
        })
    return questions


def generate_image_select_questions(phrases, vocab, unit_id):
    questions = []
    for phrase in phrases[:4]:
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
            'options': options, 'answer': key_word, 'audio_text': key_word,
        })
    return questions


def generate_scramble_questions(vocab, unit_id):
    questions = []
    for word in vocab[:4]:
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


def seed_all():
    random.seed(42)
    db = SessionLocal()
    try:
        total = 0
        # Clean existing questions for these units
        for uid in UNIT_VOCAB:
            db.query(Question).filter(Question.unit_id == uid).delete()

        for uid, data in sorted(UNIT_VOCAB.items()):
            vocab = data['vocab']
            phrases = data.get('phrases', [])
            questions = []
            questions.extend(generate_listen_questions(vocab, uid))
            questions.extend(generate_image_select_questions(phrases, vocab, uid))
            questions.extend(generate_scramble_questions(vocab, uid))
            for q in questions:
                db.add(Question(**q))
                total += 1
            print(f'Unit {uid:3d}: {len(questions)} questions')
        db.commit()
        print(f'\nTotal: {total} questions created')
    finally:
        db.close()


if __name__ == '__main__':
    seed_all()
