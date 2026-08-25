"""收集离线版全部发音文本并统计规模(edge-tts 预生成用)。"""
import hashlib
import json
import re
import sqlite3

DB = "data/english_learning.db"
db = sqlite3.connect(DB)
cur = db.cursor()

texts = set()


def add(t):
    if t and isinstance(t, str) and t.strip():
        texts.add(t.strip())


# 1. 课程配置里的发音文本
for (content,) in cur.execute("SELECT content FROM course_lessons"):
    if not content:
        continue
    steps = json.loads(content).get("steps", [])
    for s in steps:
        t = s.get("type")
        if t == "learn":
            words = s.get("words", [])
            voices = s.get("voices", {})
            examples = s.get("examples", {})
            for w in words:
                if w in voices:
                    add(voices[w])
                elif re.fullmatch(r"[A-Z]", w) and w in examples:
                    add(examples[w].replace(" · ", ". ") + ".")
                else:
                    add(w)
        elif t == "listen_tap":
            for w in s.get("words", []):
                add((s.get("voices") or {}).get(w, w))
        elif t == "listen_letter":
            for it in s.get("letters", []):
                add(it.get("sample", it.get("letter", "")))
        elif t == "spell":
            for w in s.get("words", []):
                add(w)
        elif t == "sentence":
            for it in s.get("sentences", []):
                add(it.get("text", ""))

# 2. 题库 audio_text
for (at,) in cur.execute("SELECT audio_text FROM questions WHERE audio_text IS NOT NULL"):
    add(at)

print("唯一发音文本数:", len(texts))
# 长度分布
lens = [len(x) for x in texts]
print("平均长度:", round(sum(lens) / len(lens), 1), "字符; 最长:", max(lens))
# 样例
print("样例:", list(texts)[:5])

# 预览分类
words = [x for x in texts if " " not in x]
phrases = [x for x in texts if " " in x]
print(f"单词 {len(words)} 个 / 短语句子 {len(phrases)} 个")
