"""Generate questions from Big Muzzy script vocabulary and seed the database."""
import sys
import os
import random

sys.path.insert(0, '/home/xsq/happy-learning')
from app.database import SessionLocal
from app.models import Question, QuestionType, Unit

# Episode vocabulary data (extracted from scripts)
EPISODES = [
    # Level 1
    {'episode': 1, 'unit_id': 1, 'vocab': ['please', 'plum', 'clever', 'grape', 'morning', 'thank', 'beautiful', 'strong', 'brave', 'queen', 'king', 'gardener', 'computer', 'bag', 'map', 'bike', 'motorbike', 'peach', 'hamburger', 'salad'], 'phrases': ['I\'m the King', 'I\'m the Queen', 'Good morning', 'Good afternoon', 'Good evening', 'Good night', 'How do you do', 'I\'m clever', 'I\'m brave', 'Can I have a peach please']},
    {'episode': 2, 'unit_id': 2, 'vocab': ['away', 'love', 'officer', 'take', 'come', 'prison', 'tower', 'clock', 'marry', 'headache', 'doctor', 'lunch', 'patient', 'time', 'ring', 'o\'clock', 'hungry', 'eat', 'drink', 'sleep'], 'phrases': ['I\'m in love', 'Take her away', 'Put her in the tower', 'Come here', 'What time is it']},
    {'episode': 3, 'unit_id': 2, 'vocab': ['free', 'wife', 'clock', 'prison', 'tower', 'marry', 'love', 'beautiful', 'hate', 'clever', 'computer', 'plan', 'robot', 'key', 'door', 'secret', 'garden', 'night', 'day', 'morning'], 'phrases': ['I\'m free', 'She\'s my wife', 'I hate Muzzy', 'Put her in prison', 'Good night']},
    {'episode': 4, 'unit_id': 2, 'vocab': ['ring', 'headache', 'doctor', 'lunch', 'patient', 'time', 'o\'clock', 'hungry', 'eat', 'drink', 'sleep', 'wake', 'up', 'bed', 'breakfast', 'tea', 'coffee', 'juice', 'water', 'milk'], 'phrases': ['What time is it', 'It\'s lunch time', 'Can I have some water', 'Time to eat', 'I\'m hungry']},
    {'episode': 5, 'unit_id': 2, 'vocab': ['one', 'stop', 'help', 'seven', 'go', 'come', 'fast', 'slow', 'run', 'walk', 'jump', 'sit', 'stand', 'open', 'close', 'push', 'pull', 'up', 'down', 'left'], 'phrases': ['Help me', 'Stop', 'Come here', 'Go away', 'One two three']},
    {'episode': 6, 'unit_id': 2, 'vocab': ['moon', 'star', 'sun', 'sky', 'cloud', 'rain', 'snow', 'wind', 'hot', 'cold', 'warm', 'cool', 'day', 'night', 'morning', 'evening', 'afternoon', 'today', 'tomorrow', 'yesterday'], 'phrases': ['Good morning', 'Good night', 'It\'s hot', 'It\'s cold']},
]


def generate_listen_questions(vocab: list[str], unit_id: int) -> list[dict]:
    """Generate listen-and-select questions."""
    questions = []
    for word in vocab[:8]:
        distractors = [w for w in vocab if w != word]
        random.shuffle(distractors)
        options = [word] + distractors[:3]
        random.shuffle(options)
        questions.append({
            'unit_id': unit_id,
            'type': QuestionType.LISTEN_SELECT,
            'options': options,
            'answer': word,
            'audio_text': word,
        })
    return questions


def generate_image_select_questions(phrases: list[str], unit_id: int) -> list[dict]:
    """Generate image-select-word questions."""
    questions = []
    all_words = []
    for p in phrases:
        all_words.extend(p.split())
    all_words = [w.lower().strip(".,!'\"?") for w in all_words if len(w) > 2]
    unique = list(set(all_words))

    for phrase in phrases[:5]:
        key_word = phrase.split()[-1].lower().strip(".,!'\"?")
        if len(key_word) < 3:
            key_word = phrase.split()[0].lower().strip(".,!'\"?")
        distractors = [w for w in unique if w != key_word]
        random.shuffle(distractors)
        options = [key_word] + distractors[:3]
        random.shuffle(options)
        questions.append({
            'unit_id': unit_id,
            'type': QuestionType.IMAGE_SELECT_WORD,
            'options': options,
            'answer': key_word,
            'audio_text': key_word,
        })
    return questions


def generate_scramble_questions(vocab: list[str], unit_id: int) -> list[dict]:
    """Generate scramble-word questions."""
    questions = []
    for word in vocab[:5]:
        if len(word) < 3:
            continue
        letters = list(word)
        random.shuffle(letters)
        scrambled = ''.join(letters)
        # Make sure scrambled != original
        while scrambled == word and len(word) > 1:
            random.shuffle(letters)
            scrambled = ''.join(letters)
        questions.append({
            'unit_id': unit_id,
            'type': QuestionType.SCRAMBLE_WORD,
            'options': [scrambled],
            'answer': word,
            'audio_text': word,
        })
    return questions


def seed_questions():
    random.seed(42)
    db = SessionLocal()
    try:
        total = 0
        for ep in EPISODES:
            questions = []
            questions.extend(generate_listen_questions(ep['vocab'], ep['unit_id']))
            questions.extend(generate_image_select_questions(ep.get('phrases', []), ep['unit_id']))
            questions.extend(generate_scramble_questions(ep['vocab'], ep['unit_id']))

            for q in questions:
                db.add(Question(**q))
                total += 1

        db.commit()
        print(f"Created {total} questions for {len(EPISODES)} episodes!")
    finally:
        db.close()


if __name__ == '__main__':
    seed_questions()
