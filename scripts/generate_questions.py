"""Generate questions from real textbook content for Big Muzzy and Oxford Phonics."""
import sys, os, random, json, shutil, sqlite3, re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Textbook, Unit, Question, VocabWord

random.seed(42)

db = SessionLocal()

# =====================================================================
# Big Muzzy Data
# =====================================================================

# Vocabulary extracted from video scripts, organized by episode (unit 1-12)
# Each episode maps to scenes from the video script books
MUZZY_DATA = {
    1: {  # Episodes 1-2: Introductions, greetings
        "words": [
            {"word": "king", "sentence": "I'm the King of Gondoland."},
            {"word": "queen", "sentence": "I'm the Queen."},
            {"word": "princess", "sentence": "I'm Princess Sylvia."},
            {"word": "gardener", "sentence": "I'm Bob. I'm the gardener."},
            {"word": "good", "sentence": "Good morning."},
            {"word": "morning", "sentence": "Good morning."},
            {"word": "afternoon", "sentence": "Good afternoon."},
            {"word": "evening", "sentence": "Good evening."},
            {"word": "night", "sentence": "Good night."},
            {"word": "hello", "sentence": "Hello. I'm Princess Sylvia."},
        ],
        "sentences": [
            "How do you do?",
            "I'm the King of Gondoland.",
            "Hello. I'm Bob.",
            "Good morning.",
            "Good night.",
        ],
    },
    2: {  # Episodes 3-4: Adjectives, big/small
        "words": [
            {"word": "big", "sentence": "I'm big. Big Muzzy."},
            {"word": "small", "sentence": "Small. Big. Small."},
            {"word": "strong", "sentence": "I'm strong."},
            {"word": "beautiful", "sentence": "I'm beautiful."},
            {"word": "clever", "sentence": "I'm clever."},
            {"word": "brave", "sentence": "I'm brave."},
            {"word": "bag", "sentence": "I've got a bag. A big bag."},
            {"word": "map", "sentence": "I've got a map."},
        ],
        "sentences": [
            "I'm big Muzzy.",
            "I'm strong.",
            "I'm beautiful.",
            "I'm clever.",
            "I'm brave.",
        ],
    },
    3: {  # Episodes 5-6: Food, I've got...
        "words": [
            {"word": "hamburger", "sentence": "I've got a hamburger."},
            {"word": "salad", "sentence": "Can I have a salad, please?"},
            {"word": "plum", "sentence": "I've got plums."},
            {"word": "peach", "sentence": "I've got peaches."},
            {"word": "grape", "sentence": "I've got grapes."},
            {"word": "bike", "sentence": "I've got a bike."},
            {"word": "computer", "sentence": "I've got a computer."},
            {"word": "garden", "sentence": "I've got a garden."},
        ],
        "sentences": [
            "I've got a big bag.",
            "I've got a hamburger.",
            "Can I have a peach, please?",
            "I like peaches.",
            "I like grapes.",
        ],
    },
    4: {  # Episodes 7-8: Numbers, counting
        "words": [
            {"word": "one", "sentence": "One, two, three."},
            {"word": "two", "sentence": "One, two."},
            {"word": "three", "sentence": "Three plums!"},
            {"word": "four", "sentence": "One, two, three, four."},
            {"word": "five", "sentence": "One, two, three, four, five."},
            {"word": "six", "sentence": "One, two, three, four, five, six."},
            {"word": "seven", "sentence": "One, two, three, four, five, six, seven."},
            {"word": "eight", "sentence": "One, two, three, four, five, six, seven, eight."},
            {"word": "nine", "sentence": "One, two, three, four, five, six, seven, eight, nine."},
            {"word": "ten", "sentence": "One, two, three, four, five, six, seven, eight, nine, ten."},
        ],
        "sentences": [
            "One, two, three, four, five.",
            "Three plums! Jackpot!",
            "How many trees?",
            "Count!",
            "There are ten trees.",
        ],
    },
    5: {  # Episodes 9-10: More vocabulary from L1
        "words": [
            {"word": "tree", "sentence": "How many trees? Count!"},
            {"word": "clock", "sentence": "What time is it?"},
            {"word": "eat", "sentence": "I eat clocks."},
            {"word": "hungry", "sentence": "I'm hungry."},
            {"word": "water", "sentence": "I want some water."},
            {"word": "flower", "sentence": "A beautiful flower."},
            {"word": "love", "sentence": "I love clocks."},
            {"word": "like", "sentence": "I like grapes."},
        ],
        "sentences": [
            "I eat clocks.",
            "I'm hungry.",
            "I want some water.",
            "I love clocks.",
            "How many trees?",
        ],
    },
    6: {  # Episodes 11-12: L1 finale
        "words": [
            {"word": "happy", "sentence": "I'm happy."},
            {"word": "sad", "sentence": "I'm sad."},
            {"word": "help", "sentence": "Help me!"},
            {"word": "friend", "sentence": "You're my friend."},
            {"word": "run", "sentence": "Run! Run!"},
            {"word": "stop", "sentence": "Stop!"},
            {"word": "go", "sentence": "Go! Go!"},
            {"word": "fast", "sentence": "Go fast!"},
        ],
        "sentences": [
            "I'm happy.",
            "Help me!",
            "You're my friend.",
            "Run! Run!",
            "Go fast!",
        ],
    },
    7: {  # L2 Episodes 1-2: Muzzy returns
        "words": [
            {"word": "come", "sentence": "Muzzy comes back."},
            {"word": "back", "sentence": "I'm back!"},
            {"word": "party", "sentence": "I'm going to a party."},
            {"word": "spaceship", "sentence": "I'm in my spaceship."},
            {"word": "way", "sentence": "I'm on my way."},
            {"word": "welcome", "sentence": "Welcome to Gondoland!"},
            {"word": "palace", "sentence": "That's the Palace."},
            {"word": "baby", "sentence": "She's our baby."},
        ],
        "sentences": [
            "Welcome to Gondoland!",
            "I'm going to a party.",
            "That's the Palace.",
            "She's our baby.",
            "I'm back!",
        ],
    },
    8: {  # L2 Episodes 3-4: Family, possessives
        "words": [
            {"word": "husband", "sentence": "Sylvia's husband, Bob."},
            {"word": "finger", "sentence": "They're Amanda's fingers."},
            {"word": "toe", "sentence": "They're Amanda's toes."},
            {"word": "eye", "sentence": "They're your eyes."},
            {"word": "nose", "sentence": "Your little nose."},
            {"word": "secret", "sentence": "It's a secret."},
            {"word": "surprise", "sentence": "A surprise!"},
            {"word": "wait", "sentence": "Wait and see."},
        ],
        "sentences": [
            "It's a secret.",
            "Wait and see.",
            "She's our baby.",
            "They're Amanda's fingers.",
            "A surprise!",
        ],
    },
    9: {  # L2 Episodes 5-6: Food, shopping
        "words": [
            {"word": "milk", "sentence": "What about milk?"},
            {"word": "plate", "sentence": "Get some plates."},
            {"word": "book", "sentence": "Look at the book!"},
            {"word": "read", "sentence": "You can't read."},
            {"word": "work", "sentence": "I don't like work."},
            {"word": "food", "sentence": "What food does he like?"},
            {"word": "want", "sentence": "I don't want any flowers."},
            {"word": "need", "sentence": "Do we need any milk?"},
        ],
        "sentences": [
            "What about milk?",
            "I don't like work.",
            "You can't read.",
            "I don't want any flowers.",
            "Do we need any milk?",
        ],
    },
    10: {  # L2 Episodes 7-8: Prepositions, locations
        "words": [
            {"word": "inside", "sentence": "Is there anyone inside?"},
            {"word": "outside", "sentence": "Go outside!"},
            {"word": "over", "sentence": "Over there."},
            {"word": "front", "sentence": "In front of you."},
            {"word": "behind", "sentence": "Behind you."},
            {"word": "box", "sentence": "Take this box!"},
            {"word": "button", "sentence": "Push the button!"},
            {"word": "careful", "sentence": "Be careful!"},
        ],
        "sentences": [
            "Is there anyone inside?",
            "Over there.",
            "In front of you.",
            "Push the button!",
            "Be careful!",
        ],
    },
    11: {  # L2 Episodes 9-10: Action verbs
        "words": [
            {"word": "dance", "sentence": "Let's dance!"},
            {"word": "sing", "sentence": "Let's sing!"},
            {"word": "play", "sentence": "Let's play!"},
            {"word": "swim", "sentence": "I can swim."},
            {"word": "fly", "sentence": "I can fly!"},
            {"word": "jump", "sentence": "I can jump!"},
            {"word": "climb", "sentence": "I can climb."},
            {"word": "sleep", "sentence": "Time to sleep."},
        ],
        "sentences": [
            "Let's dance!",
            "I can swim.",
            "I can fly!",
            "I can jump!",
            "Time to sleep.",
        ],
    },
    12: {  # L2 Episodes 11-12: Finale
        "words": [
            {"word": "goodbye", "sentence": "Goodbye, Muzzy!"},
            {"word": "thank", "sentence": "Thank you!"},
            {"word": "sorry", "sentence": "I'm sorry."},
            {"word": "please", "sentence": "Can I have one, please?"},
            {"word": "forever", "sentence": "Forever and ever."},
            {"word": "together", "sentence": "All together!"},
            {"word": "wonderful", "sentence": "How wonderful!"},
            {"word": "amazing", "sentence": "That's amazing!"},
        ],
        "sentences": [
            "Goodbye, Muzzy!",
            "Thank you!",
            "Forever and ever.",
            "All together!",
            "How wonderful!",
        ],
    },
}

# =====================================================================
# Oxford Phonics Data (from OCR of Student Books)
# =====================================================================

PHONICS_DATA = {
    1: {  # Level 1: Letter sounds a-z
        "name": "Level 1 - Letter Sounds",
        "letters": {
            "a": ["apple", "ant", "alligator"],
            "b": ["bear", "ball", "bed"],
            "c": ["cat", "cup", "car"],
            "d": ["dog", "doll", "door"],
            "e": ["egg", "elephant", "envelope"],
            "f": ["fish", "frog", "fan"],
            "g": ["gorilla", "goat", "gift"],
            "h": ["horse", "hat", "house"],
            "i": ["insect", "igloo", "ink"],
            "j": ["jet", "jar", "jam"],
            "k": ["kangaroo", "kite", "key"],
            "l": ["lion", "lamp", "leaf"],
            "m": ["monkey", "moon", "mouse"],
            "n": ["nut", "net", "nose"],
            "o": ["octopus", "orange", "owl"],
            "p": ["pig", "pen", "pan"],
            "q": ["queen", "quilt", "quiet"],
            "r": ["rabbit", "ring", "rain"],
            "s": ["sun", "star", "snake"],
            "t": ["tiger", "tree", "tent"],
            "u": ["umbrella", "uncle", "up"],
            "v": ["van", "vest", "violin"],
            "w": ["whale", "watch", "wolf"],
            "x": ["box", "fox", "six"],
            "y": ["yak", "yarn", "yellow"],
            "z": ["zebra", "zoo", "zip"],
        },
    },
    2: {  # Level 2: CVC words
        "name": "Level 2 - CVC Words",
        "groups": [
            {"pattern": "-at", "words": ["cat", "bat", "hat", "mat", "rat", "sat"]},
            {"pattern": "-og", "words": ["dog", "log", "fog", "hog", "jog"]},
            {"pattern": "-en", "words": ["pen", "hen", "ten", "men", "den"]},
            {"pattern": "-ig", "words": ["pig", "big", "wig", "dig", "fig"]},
            {"pattern": "-un", "words": ["sun", "run", "fun", "bun", "pun"]},
            {"pattern": "-ed", "words": ["bed", "red", "fed", "led"]},
            {"pattern": "-ap", "words": ["map", "cap", "tap", "nap", "lap"]},
            {"pattern": "-in", "words": ["pin", "bin", "fin", "win", "tin"]},
            {"pattern": "-ot", "words": ["pot", "hot", "cot", "dot", "lot"]},
            {"pattern": "-ug", "words": ["bug", "rug", "mug", "jug", "tug"]},
        ],
    },
    3: {  # Level 3: Consonant blends
        "name": "Level 3 - Consonant Blends",
        "groups": [
            {"pattern": "bl-", "words": ["black", "blue", "block", "blob", "blow"]},
            {"pattern": "cl-", "words": ["clap", "clock", "club", "climb", "clip"]},
            {"pattern": "fl-", "words": ["flag", "flower", "fly", "flap", "flat"]},
            {"pattern": "gl-", "words": ["glass", "glow", "glue", "glove", "globe"]},
            {"pattern": "pl-", "words": ["plane", "plant", "play", "plate", "plus"]},
            {"pattern": "sl-", "words": ["sleep", "slide", "slow", "slip", "slug"]},
            {"pattern": "br-", "words": ["brown", "brick", "brush", "bread", "broom"]},
            {"pattern": "cr-", "words": ["crab", "crop", "cry", "crack", "crew"]},
            {"pattern": "dr-", "words": ["dress", "drag", "drop", "drum", "drink"]},
            {"pattern": "fr-", "words": ["frog", "fruit", "frock", "fry", "fresh"]},
            {"pattern": "gr-", "words": ["grape", "grass", "green", "grow", "grin"]},
            {"pattern": "tr-", "words": ["tree", "train", "truck", "trap", "trip"]},
        ],
    },
    4: {  # Level 4: Vowel teams
        "name": "Level 4 - Vowel Teams",
        "groups": [
            {"pattern": "ai", "words": ["rain", "train", "paint", "mail", "tail"]},
            {"pattern": "ay", "words": ["day", "play", "say", "way", "stay"]},
            {"pattern": "ee", "words": ["bee", "tree", "see", "bee", "feet"]},
            {"pattern": "ea", "words": ["eat", "leaf", "sea", "tea", "read"]},
            {"pattern": "oa", "words": ["boat", "coat", "goat", "road", "soap"]},
            {"pattern": "ow", "words": ["cow", "now", "how", "brown", "clown"]},
            {"pattern": "oi", "words": ["coin", "boil", "soil", "foil", "noise"]},
            {"pattern": "oy", "words": ["boy", "toy", "joy", "soy", "oyster"]},
            {"pattern": "ou", "words": ["house", "mouse", "cloud", "mouth", "out"]},
            {"pattern": "ie", "words": ["pie", "tie", "die", "lie", "cries"]},
        ],
    },
    5: {  # Level 5: Complex patterns
        "name": "Level 5 - Complex Patterns",
        "groups": [
            {"pattern": "ar", "words": ["car", "star", "park", "farm", "dark"]},
            {"pattern": "or", "words": ["fork", "pork", "corn", "storm", "born"]},
            {"pattern": "ir", "words": ["bird", "shirt", "girl", "first", "dirt"]},
            {"pattern": "ur", "words": ["turn", "burn", "nurse", "purse", "fur"]},
            {"pattern": "er", "words": ["her", "fern", "term", "nerve", "verb"]},
            {"pattern": "igh", "words": ["night", "light", "high", "right", "sight"]},
            {"pattern": "ough", "words": ["cough", "bough", "dough", "tough", "rough"]},
            {"pattern": "tion", "words": ["action", "motion", "station", "nation", "option"]},
            {"pattern": "sion", "words": ["vision", "mission", "passion", "fusion", "tension"]},
            {"pattern": "ture", "words": ["nature", "future", "picture", "capture", "creature"]},
        ],
    },
}

# =====================================================================
# Word card image mapping
# =====================================================================

WORD_CARD_DIR = "data/word_cards"


def find_word_image(word):
    """Find existing word card image for a word."""
    word_lower = word.lower()
    # Use the existing combined_word_to_image mapping
    mapping_path = "data/combined_word_to_image.json"
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        img = mapping.get(word_lower, "")
        if img:
            return img
    # Fallback: generate a pollinations URL
    return f"https://image.pollinations.ai/prompt=simple+cartoon+illustration+of+{word}+for+kids?width=300&height=300&nologo=true"


def phonics_image(level, page_num):
    """Get phonics image path for a level and page."""
    return f"/phonics/level_{level}/page_{page_num:03d}.png"


def get_available_images_for_unit(unit_num):
    """Get all available images for a given Muzzy unit."""
    unit_dir = os.path.join(WORD_CARD_DIR, f"{unit_num:02d}")
    images = []
    if os.path.isdir(unit_dir):
        for f in sorted(os.listdir(unit_dir)):
            if f.endswith(('.png', '.jpg', '.jpeg')):
                images.append(f"/word-cards/{unit_num:02d}/{f}")
    return images


# =====================================================================
# Question Generation Helpers
# =====================================================================

def make_distractors(correct_word, all_words, count=3):
    """Pick random distractor words."""
    others = [w for w in all_words if w.lower() != correct_word.lower()]
    random.shuffle(others)
    return others[:count]


def make_options(correct, distractors):
    """Shuffle correct answer among distractors."""
    opts = [correct] + distractors
    random.shuffle(opts)
    return opts


# =====================================================================
# Big Muzzy Question Generation
# =====================================================================

def generate_muzzy_questions():
    """Generate all questions for Big Muzzy textbook."""
    muzzy = db.query(Textbook).filter(Textbook.name.like("Big Muzzy%")).first()
    if not muzzy:
        print("ERROR: Big Muzzy textbook not found!")
        return

    # Collect all words across all units for distractors
    all_muzzy_words = []
    for unit_data in MUZZY_DATA.values():
        all_muzzy_words.extend([w["word"] for w in unit_data["words"]])

    units = db.query(Unit).filter(Unit.textbook_id == muzzy.id).order_by(Unit.order).all()

    for unit in units:
        unit_num = unit.order
        data = MUZZY_DATA.get(unit_num)
        if not data:
            continue

        unit_words = [w["word"] for w in data["words"]]
        unit_sentences = data["sentences"]
        images = get_available_images_for_unit(unit_num)
        word_to_image = {}
        for w in data["words"]:
            img = find_word_image(w["word"])
            if img:
                word_to_image[w["word"]] = img

        questions_created = 0

        # 1. Image Select Word - use word card images
        for i, w in enumerate(data["words"][:min(8, len(data["words"]))]):
            distractors = make_distractors(w["word"], all_muzzy_words)
            image_url = word_to_image.get(w["word"], "")
            db.add(Question(
                textbook_id=muzzy.id,
                unit_id=unit.id,
                type="image_select_word",
                difficulty=1,
                options=make_options(w["word"], distractors),
                answer=w["word"],
                image_url=image_url,
                audio_text=w["word"],
                sentence=w["sentence"],
            ))
            questions_created += 1

        # 2. Listen Select - audio-based word selection
        for i, w in enumerate(data["words"][:min(5, len(data["words"]))]):
            distractors = make_distractors(w["word"], all_muzzy_words)
            db.add(Question(
                textbook_id=muzzy.id,
                unit_id=unit.id,
                type="listen_select",
                difficulty=1,
                options=make_options(w["word"], distractors),
                answer=w["word"],
                audio_text=w["word"],
            ))
            questions_created += 1

        # 3. Listen Spell - spell the word after hearing
        for i, w in enumerate(data["words"][:min(4, len(data["words"]))]):
            if len(w["word"]) < 3:
                continue
            db.add(Question(
                textbook_id=muzzy.id,
                unit_id=unit.id,
                type="listen_spell",
                difficulty=2,
                options=[w["word"]],  # answer for validation
                answer=w["word"],
                audio_text=w["word"],
                sentence=w["sentence"],
            ))
            questions_created += 1

        # 4. Image Select Sentence - choose matching sentence for scene
        for i, sentence in enumerate(unit_sentences[:min(3, len(unit_sentences))]):
            distractor_sents = [s for s in all_muzzy_sentences(muzzy) if s != sentence]
            random.shuffle(distractor_sents)
            distractors = distractor_sents[:2]
            db.add(Question(
                textbook_id=muzzy.id,
                unit_id=unit.id,
                type="image_select_sentence",
                difficulty=2,
                options=make_options(sentence, distractors),
                answer=sentence,
                image_url=images[i % len(images)] if images else "",
                audio_text=sentence,
                sentence=sentence,
            ))
            questions_created += 1

        # 5. Listen Spell Sentence - word ordering with 1 distractor
        for i, sentence in enumerate(unit_sentences[:min(3, len(unit_sentences))]):
            sentence_words = sentence.split()
            other_words = []
            for s in unit_sentences:
                if s != sentence:
                    for w in s.split():
                        if w not in sentence_words and w not in other_words:
                            other_words.append(w)
            random.shuffle(other_words)
            distractor = other_words[:1] if other_words else []
            options = sentence_words + distractor
            db.add(Question(
                textbook_id=muzzy.id,
                unit_id=unit.id,
                type="listen_spell_sentence",
                difficulty=3,
                options=options,
                answer=sentence,
                audio_text=sentence,
                sentence=sentence,
            ))
            questions_created += 1

        # 6. Image Listen Spell Sentence - image + audio + word ordering with 1 distractor
        for i, w in enumerate(data["words"]):
            sentence = w["sentence"]
            sentence_words = sentence.split()
            # Pick 1 distractor word from other sentences
            other_words = []
            for s in unit_sentences:
                if s != sentence:
                    for w2 in s.split():
                        if w2 not in sentence_words and w2 not in other_words:
                            other_words.append(w2)
            random.shuffle(other_words)
            distractor = other_words[:1] if other_words else []
            options = sentence_words + distractor
            image_url = word_to_image.get(w["word"], "")
            if not image_url:
                image_url = find_word_image(w["word"])
            db.add(Question(
                textbook_id=muzzy.id,
                unit_id=unit.id,
                type="image_listen_spell_sentence",
                difficulty=3,
                options=options,
                answer=sentence,
                image_url=image_url,
                audio_text=sentence,
                sentence=sentence,
            ))
            questions_created += 1

        print(f"  Big Muzzy Unit {unit_num} ({unit.name}): {questions_created} questions")

    db.commit()


def all_muzzy_sentences(muzzy):
    """Get all sentences from all Muzzy units."""
    sentences = []
    for data in MUZZY_DATA.values():
        sentences.extend(data["sentences"])
    return list(set(sentences))


# =====================================================================
# Oxford Phonics Question Generation
# =====================================================================

def generate_phonics_questions():
    """Generate all questions for Oxford Phonics textbook."""
    phonics = db.query(Textbook).filter(Textbook.name.like("Oxford Phonics%")).first()
    if not phonics:
        print("ERROR: Oxford Phonics textbook not found!")
        return

    units = db.query(Unit).filter(Unit.textbook_id == phonics.id).order_by(Unit.order).all()

    for unit in units:
        level = unit.order
        data = PHONICS_DATA.get(level)
        if not data:
            continue

        # Collect all words at this level for distractors
        level_words = []
        if level == 1:
            for words in data["letters"].values():
                level_words.extend(words)
        else:
            for group in data["groups"]:
                level_words.extend(group["words"])

        # Also collect all words from other levels for cross-level distractors
        all_phonics_words = []
        for ldata in PHONICS_DATA.values():
            if ldata.get("letters"):
                for ws in ldata["letters"].values():
                    all_phonics_words.extend(ws)
            if ldata.get("groups"):
                for g in ldata["groups"]:
                    all_phonics_words.extend(g["words"])

        questions_created = 0

        if level == 1:
            # Level 1: Letter sounds - questions about individual letters
            letter_list = list(data["letters"].items())
            for idx, (letter, words) in enumerate(letter_list):
                page_base = 6 + idx * 2  # pages with vocabulary images
                for wi, word in enumerate(words[:2]):
                    distractors = make_distractors(word, all_phonics_words)
                    img = phonics_image(level, page_base + wi)
                    db.add(Question(
                        textbook_id=phonics.id,
                        unit_id=unit.id,
                        type="image_select_word",
                        difficulty=1,
                        options=make_options(word, distractors),
                        answer=word,
                        image_url=img,
                        audio_text=word,
                    ))
                    questions_created += 1

                # Listen select for each letter's primary word
                if words:
                    word = words[0]
                    distractors = make_distractors(word, all_phonics_words)
                    db.add(Question(
                        textbook_id=phonics.id,
                        unit_id=unit.id,
                        type="listen_select",
                        difficulty=1,
                        options=make_options(word, distractors),
                        answer=word,
                        audio_text=word,
                    ))
                    questions_created += 1

                # Listen spell for primary word
                if words and len(words[0]) >= 3:
                    word = words[0]
                    db.add(Question(
                        textbook_id=phonics.id,
                        unit_id=unit.id,
                        type="listen_spell",
                        difficulty=2,
                        options=[word],
                        answer=word,
                        audio_text=word,
                    ))
                    questions_created += 1

        else:
            # Levels 2-5: Pattern-based questions
            for gi, group in enumerate(data["groups"]):
                pattern = group["pattern"]
                page_base = 4 + gi * 3
                for wi, word in enumerate(group["words"][:3]):
                    distractors = make_distractors(word, all_phonics_words)
                    img = phonics_image(level, page_base + wi)
                    db.add(Question(
                        textbook_id=phonics.id,
                        unit_id=unit.id,
                        type="image_select_word",
                        difficulty=1 if level <= 3 else 2,
                        options=make_options(word, distractors),
                        answer=word,
                        image_url=img,
                        audio_text=word,
                    ))
                    questions_created += 1

                    # Listen select
                    distractors2 = make_distractors(word, all_phonics_words)
                    db.add(Question(
                        textbook_id=phonics.id,
                        unit_id=unit.id,
                        type="listen_select",
                        difficulty=1 if level <= 3 else 2,
                        options=make_options(word, distractors2),
                        answer=word,
                        audio_text=word,
                    ))
                    questions_created += 1

                    # Listen spell
                    if len(word) >= 3:
                        db.add(Question(
                            textbook_id=phonics.id,
                            unit_id=unit.id,
                            type="listen_spell",
                            difficulty=2 if level <= 3 else 3,
                            options=[word],
                            answer=word,
                            audio_text=word,
                        ))
                        questions_created += 1

                # Image select sentence with pattern example
                if group["words"]:
                    example = f"The {group['words'][0]} is {pattern}."
                    img = phonics_image(level, page_base + 3)
                    db.add(Question(
                        textbook_id=phonics.id,
                        unit_id=unit.id,
                        type="image_select_sentence",
                        difficulty=2 if level <= 3 else 3,
                        options=[example],
                        answer=example,
                        image_url=img,
                        audio_text=example,
                        sentence=example,
                    ))
                    questions_created += 1

        print(f"  Phonics {data['name']}: {questions_created} questions")

    db.commit()


# =====================================================================
# Main
# =====================================================================

if __name__ == "__main__":
    print("=== Generating Questions ===")

    # Clear existing questions
    db.query(Question).delete()
    db.commit()
    print("Cleared existing questions.")

    print("\nGenerating Big Muzzy questions...")
    generate_muzzy_questions()

    print("\nGenerating Oxford Phonics questions...")
    generate_phonics_questions()

    # Summary
    total = db.query(Question).count()
    print(f"\n=== Summary: {total} questions ===")

    c = sqlite3.connect("data/english_learning.db")
    cur = c.cursor()
    cur.execute("""
        SELECT t.name, q.type, COUNT(*)
        FROM questions q
        JOIN textbooks t ON q.textbook_id = t.id
        GROUP BY t.name, q.type
        ORDER BY t.name, q.type
    """)
    for row in cur.fetchall():
        print(f"  {row[0]} | {row[1]}: {row[2]}")
    cur.close()

    db.close()
    print("\nDone!")
