"""Parse Big Muzzy script text files into per-episode scripts with extracted vocabulary."""
import re
import json
import os

# Common stop words to filter out
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
    'might', 'shall', 'can', 'need', 'must', 'i', 'you', 'he', 'she', 'it',
    'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his',
    'our', 'their', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when',
    'how', 'why', 'not', 'no', 'yes', 'so', 'if', 'then', 'than', 'too',
    'very', 'just', 'also', 'only', 'about', 'up', 'out', 'of', 'with',
    'by', 'from', 'as', 'that', 'this', 'these', 'those', 'here', 'there',
    'now', 'don', 't', 's', 'm', 'll', 'd', 've', 're', 'oh',
    'big', 'small', 'good', 'bad', 'new', 'old', 'hello', 'hi',
}

# Character names to filter out (appear on left side of dialogue)
CHARACTER_NAMES = {
    'king', 'queen', 'sylvia', 'bob', 'corvax', 'muzzy', 'norman',
    'cat', 'computer', 'waiter', 'thimbo', 'police', 'sun', 'moon',
    'mrs', 'guard', 'guards', 'narrator',
}


def split_parts(filepath: str) -> list[dict]:
    """Split a script file into parts (episodes)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Split by "Part N" pattern
    parts = re.split(r'\n\s+Part\s+(\d+)\s+', text)
    # parts[0] is preamble, then alternating [number, content, number, content...]

    results = []
    i = 1
    while i < len(parts):
        num = int(parts[i])
        content = parts[i + 1] if i + 1 < len(parts) else ''
        results.append({'part': num, 'text': content.strip()})
        i += 2
    return results


def extract_vocabulary(text: str, top_n: int = 15) -> list[str]:
    """Extract key vocabulary words from script text."""
    # Find all words
    words = re.findall(r"[a-zA-Z]+(?:'[a-z]+)?", text.lower())
    # Filter: only content words (not stop words, not single letters, min 2 chars)
    words = [w for w in words if w not in STOP_WORDS and len(w) >= 2 and w not in CHARACTER_NAMES]

    # Count frequency
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    # Sort by frequency, return top N
    sorted_words = sorted(freq.items(), key=lambda x: -x[1])
    return [w for w, _ in sorted_words[:top_n]]


def extract_phrases(text: str) -> list[str]:
    """Extract useful phrases from the script."""
    phrases = []
    # Look for common patterns
    # "I'm the..." / "I've got..." / "Can I have..."
    patterns = [
        r"(I'm\s+[\w\s]+?)(?:\.|,|\n)",
        r"(I've got\s+[\w\s]+?)(?:\.|,|\n)",
        r"(Can I have\s+[\w\s]+?please)",
        r"(Good\s+(morning|afternoon|evening|night))",
        r"(How do you do)",
        r"(Here you are)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            phrase = m[0] if isinstance(m, tuple) else m
            phrase = phrase.strip().rstrip('.')
            if len(phrase) > 5 and phrase not in phrases:
                phrases.append(phrase)
    return phrases[:10]


def parse_all():
    scripts_dir = '/home/xsq/happy-learning/data/scripts'
    output_dir = '/home/xsq/happy-learning/data/scripts'

    all_episodes = []

    # Parse Level 1 (Parts 1-6 -> Episodes 1-6)
    l1_parts = split_parts(os.path.join(scripts_dir, 'muzzy_script_l1.txt'))
    for p in l1_parts:
        vocab = extract_vocabulary(p['text'])
        phrases = extract_phrases(p['text'])
        episode = {
            'level': 1,
            'episode': p['part'],
            'title': f'Part {p["part"]}',
            'vocab': vocab,
            'phrases': phrases,
        }
        all_episodes.append(episode)

    # Parse Level 2 (Parts 1-6 -> Episodes 7-12)
    l2_parts = split_parts(os.path.join(scripts_dir, 'muzzy_script_l2.txt'))
    for p in l2_parts:
        vocab = extract_vocabulary(p['text'])
        phrases = extract_phrases(p['text'])
        episode = {
            'level': 2,
            'episode': p['part'] + 6,
            'title': f'Part {p["part"]}',
            'vocab': vocab,
            'phrases': phrases,
        }
        all_episodes.append(episode)

    # Save per-episode text files
    for ep in all_episodes:
        filepath = os.path.join(output_dir, f'muzzy_ep{ep["episode"]}_vocab.txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Big Muzzy Episode {ep['episode']} (Level {ep['level']}, {ep['title']})\n")
            f.write(f"\nKey Vocabulary:\n")
            for v in ep['vocab']:
                f.write(f"  - {v}\n")
            f.write(f"\nKey Phrases:\n")
            for ph in ep['phrases']:
                f.write(f"  - {ph}\n")

    # Save all as JSON
    with open(os.path.join(output_dir, 'muzzy_episodes.json'), 'w', encoding='utf-8') as f:
        json.dump(all_episodes, f, indent=2, ensure_ascii=False)

    return all_episodes


if __name__ == '__main__':
    episodes = parse_all()
    for ep in episodes:
        print(f"Episode {ep['episode']}: {', '.join(ep['vocab'][:8])}")
