#!/usr/bin/env python3
"""Extract images and word/sentence pairs from Big Muzzy vocabulary card .doc files."""

import re
import json
import html
import subprocess
import zipfile
from pathlib import Path

DOC_DIR = Path("/mnt/f/1.英语启蒙/Big Muzzy 玛泽的故事/07、单词图卡可打印")
OUTPUT_DIR = Path("/home/xsq/happy-learning/data/muzzy_word_cards")
WORK_DIR = Path("/tmp/muzzy_extract_work")


def convert_doc_to_odt(doc_path: Path, work_dir: Path) -> Path | None:
    """Convert .doc to .odt using LibreOffice headless mode."""
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "odt", str(doc_path)],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
        timeout=120,
    )
    odt_path = work_dir / f"{doc_path.stem}.odt"
    return odt_path if odt_path.exists() else None


def extract_text_from_cell(cell: str) -> list[str]:
    """Extract plain text from a cell, handling both text:h and text:p."""
    texts = []
    for tag in ["text:h", "text:p"]:
        matches = re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>", cell, re.DOTALL)
        for tm in matches:
            plain = re.sub(r"<[^>]+>", "", tm).strip()
            if plain:
                texts.append(plain)
    return texts


def extract_pairs_from_odt(odt_path: Path, file_prefix: str) -> list[dict]:
    """Extract image-text pairs from an ODT file.

    Structure: alternating cells where even cells contain images and odd cells
    contain text. Each image corresponds to ALL text items in the following cell.
    """
    z = zipfile.ZipFile(odt_path)
    content = z.read("content.xml").decode("utf-8")

    cell_pattern = r"<table:table-cell[^>]*>(.*?)</table:table-cell>"
    cells = re.findall(cell_pattern, content, re.DOTALL)

    pairs = []
    pending_image = None

    for cell in cells:
        img_match = re.search(
            r'<draw:frame[^>]*draw:name="[^"]*"[^>]*>.*?xlink:href="([^"]*)"',
            cell,
            re.DOTALL,
        )
        has_img = img_match is not None
        cell_texts = extract_text_from_cell(cell)

        if has_img:
            pending_image = img_match.group(1)
        elif cell_texts and pending_image:
            for t in cell_texts:
                pairs.append({
                    "text": t,
                    "image": pending_image,
                    "file": file_prefix,
                })
            pending_image = None

    return pairs


def extract_images(odt_path: Path, dest_dir: Path, used_images: set) -> None:
    """Extract only the images that are referenced in pairs."""
    z = zipfile.ZipFile(odt_path)
    for name in z.namelist():
        if name.startswith("Pictures/") and name in used_images:
            dest = dest_dir / Path(name).name
            if not dest.exists():
                dest.write_bytes(z.read(name))


def is_sentence(text: str) -> bool:
    """Classify text as sentence vs word."""
    text = text.strip()
    if text.endswith((".", "!", "?")):
        return True
    sentence_words = [
        "i'm", "she's", "he's", "it's", "they're", "we're", "you're",
        "i've", "there's", "there", "don't", "doesn't", "didn't",
        "isn't", "aren't", "wasn't", "won't", "wouldn't", "shouldn't",
        "can't", "couldn't",
    ]
    lower = text.lower()
    if any(lower.startswith(w) for w in sentence_words):
        return True
    if any(w in lower for w in ["somebody", "nothing", "anything"]):
        return True
    return False


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    images_dir = OUTPUT_DIR / "images"
    images_dir.mkdir(exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    for f in WORK_DIR.iterdir():
        f.unlink()

    doc_files = sorted(f for f in DOC_DIR.glob("*.doc") if not f.name.startswith("~$"))
    print(f"Found {len(doc_files)} .doc files")

    all_pairs = []
    all_used_images = set()

    for i, doc_file in enumerate(doc_files):
        print(f"\n[{i+1}/{len(doc_files)}] Processing {doc_file.name}...")

        odt_path = convert_doc_to_odt(doc_file, WORK_DIR)
        if not odt_path:
            print(f"  FAILED to convert {doc_file.name}")
            continue

        file_prefix = doc_file.name.replace("Big Muzzy单词图卡", "").replace(".doc", "").strip("_")

        pairs = extract_pairs_from_odt(odt_path, file_prefix)
        print(f"  Found {len(pairs)} image-text pairs")

        for p in pairs:
            all_used_images.add(p["image"])

        extract_images(odt_path, images_dir, all_used_images)
        all_pairs.extend(pairs)
        odt_path.unlink(missing_ok=True)

    # Decode HTML entities
    for p in all_pairs:
        p["text"] = html.unescape(p["text"])

    # Deduplicate: keep first occurrence of each (text, image) pair
    seen = set()
    unique_pairs = []
    for p in all_pairs:
        key = (p["text"], Path(p["image"]).name)
        if key not in seen:
            seen.add(key)
            unique_pairs.append(p)

    print(f"\nTotal pairs: {len(all_pairs)}, unique: {len(unique_pairs)}")

    # Classify
    words = [p for p in unique_pairs if not is_sentence(p["text"])]
    sentences = [p for p in unique_pairs if is_sentence(p["text"])]

    # Save master JSON
    master = {
        "total": len(unique_pairs),
        "words_count": len(words),
        "sentences_count": len(sentences),
        "cards": unique_pairs,
        "words": words,
        "sentences": sentences,
    }

    with open(OUTPUT_DIR / "word_cards.json", "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)

    # Simplified format for quiz app
    simplified = []
    for idx, card in enumerate(unique_pairs, 1):
        simplified.append({
            "id": idx,
            "text": card["text"],
            "image": f"images/{Path(card['image']).name}",
            "type": "sentence" if is_sentence(card["text"]) else "word",
        })

    with open(OUTPUT_DIR / "cards.json", "w", encoding="utf-8") as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {OUTPUT_DIR}/")
    print(f"  word_cards.json (full data)")
    print(f"  cards.json (simplified for quiz app)")
    print(f"  images/ ({len(list(images_dir.glob('*')))} images)")

    print(f"\nWords: {len(words)}, Sentences: {len(sentences)}")
    print("\nSample words:")
    for w in words[:10]:
        print(f"  '{w['text']}' -> {Path(w['image']).name}")
    print("\nSample sentences:")
    for s in sentences[:10]:
        print(f"  '{s['text']}' -> {Path(s['image']).name}")


if __name__ == "__main__":
    main()
