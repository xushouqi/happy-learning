"""预生成离线版全部发音音频(edge-tts 神经网络语音)。

输出:frontend/public/audio/{md5}.mp3 + frontend/src/offline/audio-map.js
用法:python3 scripts/generate_offline_audio.py
"""
import asyncio
import hashlib
import json
import os
import re
import sqlite3

import edge_tts

VOICE = "en-US-JennyNeural"  # 微软神经语音(自然柔和),可选 en-US-GuyNeural(男声)
RATE = "+0%"
AUDIO_DIR = "frontend/public/audio"
MAP_PATH = "frontend/src/offline/audio-map.js"
DB = "data/english_learning.db"

os.makedirs(AUDIO_DIR, exist_ok=True)


def norm(t):
    return re.sub(r"\s+", " ", t.strip().lower())


def collect_texts():
    db = sqlite3.connect(DB)
    cur = db.cursor()
    texts = set()

    def add(t):
        if t and isinstance(t, str) and t.strip():
            texts.add(t.strip())

    for (content,) in cur.execute("SELECT content FROM course_lessons"):
        if not content:
            continue
        for s in json.loads(content).get("steps", []):
            st = s.get("type")
            if st == "learn":
                voices = s.get("voices", {})
                examples = s.get("examples", {})
                for w in s.get("words", []):
                    if w in voices:
                        add(voices[w])
                    elif re.fullmatch(r"[A-Z]", w) and w in examples:
                        add(examples[w].replace(" · ", ". ") + ".")
                    else:
                        add(w)
            elif st == "listen_tap":
                for w in s.get("words", []):
                    add((s.get("voices") or {}).get(w, w))
            elif st == "listen_letter":
                for it in s.get("letters", []):
                    add(it.get("sample", it.get("letter", "")))
            elif st == "spell":
                for w in s.get("words", []):
                    add(w)
            elif st == "sentence":
                for it in s.get("sentences", []):
                    add(it.get("text", ""))
    for (at,) in cur.execute("SELECT audio_text FROM questions WHERE audio_text IS NOT NULL"):
        add(at)
    return texts


async def gen(text, out):
    c = edge_tts.Communicate(text, voice=VOICE, rate=RATE)
    await c.save(out)


async def main():
    texts = collect_texts()
    print(f"唯一文本: {len(texts)}")

    audio_map = {}
    todo = []
    for t in texts:
        key = norm(t)
        fname = hashlib.md5(key.encode()).hexdigest() + ".mp3"
        path = os.path.join(AUDIO_DIR, fname)
        audio_map[key] = fname
        if not os.path.exists(path):
            todo.append((t, path))

    print(f"待生成: {len(todo)} / 已有: {len(texts) - len(todo)}")

    sem = asyncio.Semaphore(8)
    done = 0

    async def limited(t, p):
        nonlocal done
        async with sem:
            await gen(t, p)
        done += 1
        if done % 50 == 0:
            print(f"  进度 {done}/{len(todo)}")

    await asyncio.gather(*[limited(t, p) for t, p in todo])

    # 写内嵌映射
    with open(MAP_PATH, "w", encoding="utf-8") as f:
        f.write("// 自动生成:发音文本→音频文件映射(scripts/generate_offline_audio.py)\n")
        f.write("export const AUDIO_MAP = ")
        json.dump(audio_map, f, ensure_ascii=False)
        f.write("\n")

    total_mb = sum(os.path.getsize(os.path.join(AUDIO_DIR, f)) for f in os.listdir(AUDIO_DIR)) / 1048576
    print(f"完成,共 {len(audio_map)} 条映射,音频总大小 {total_mb:.1f}MB")


if __name__ == "__main__":
    asyncio.run(main())
