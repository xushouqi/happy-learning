import random
from app.models import Question, QuestionType


def generate_listen_questions(extracted_words: list[str], unit_id: int) -> list[dict]:
    """Generate listen-and-select questions from vocabulary."""
    questions = []
    for word in extracted_words[:5]:
        distractors = [w for w in extracted_words if w != word]
        options = [word] + random.sample(distractors, min(3, len(distractors)))
        random.shuffle(options)
        questions.append({
            'unit_id': unit_id,
            'type': QuestionType.LISTEN_SELECT,
            'options': options,
            'answer': word,
            'audio_text': word,
        })
    return questions


def generate_scramble_questions(extracted_words: list[str], unit_id: int) -> list[dict]:
    """Generate scramble-word questions."""
    questions = []
    for word in extracted_words[:3]:
        if len(word) < 3:
            continue
        letters = list(word)
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
