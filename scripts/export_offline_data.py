"""导出 happy-learning 离线数据(课程/教材/单词/用户)为 JSON,供安卓离线版使用。

用法:python3 scripts/export_offline_data.py
输出:frontend/public/data/{textbooks,courses,vocab_words,users}.json
"""
import json
import os
import sqlite3

DB = "data/english_learning.db"
OUT = "frontend/public/data"

os.makedirs(OUT, exist_ok=True)
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()


def dump(name, rows):
    data = [dict(r) for r in rows]
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"{name}: {len(data)} 条, {os.path.getsize(path)//1024} KB")


# 教材(含单元)
textbooks = []
for tb in cur.execute('SELECT id, name, source_path, cover_image, status FROM textbooks ORDER BY id'):
    cur2 = db.cursor()
    units = cur2.execute(
        'SELECT id, textbook_id, name, "order", video_path FROM units WHERE textbook_id=? ORDER BY "order"',
        (tb["id"],),
    ).fetchall()
    cur2.close()
    textbooks.append({**dict(tb), "units": [dict(u) for u in units]})
dump("textbooks.json", textbooks)

# 课程(含课时内容)
courses = []
for c in cur.execute('SELECT id, textbook_id, unit_id, title, description, cover_emoji, "order", status FROM courses ORDER BY "order", id'):
    cur2 = db.cursor()
    lessons = cur2.execute(
        'SELECT id, course_id, title, subtitle, "order", content FROM course_lessons WHERE course_id=? ORDER BY "order"',
        (c["id"],),
    ).fetchall()
    cur2.close()
    lessons_out = []
    for l in lessons:
        d = dict(l)
        d["content"] = json.loads(d["content"]) if d["content"] else {}
        lessons_out.append(d)
    courses.append({**dict(c), "lessons": lessons_out})
dump("courses.json", courses)

# 单词(用于内容组装时查图)
dump("vocab_words.json", cur.execute("SELECT id, textbook_id, unit_id, word, image_path, example_sentence FROM vocab_words").fetchall())

# 用户(默认用户列表)
users = cur.execute("SELECT id, name, avatar FROM users ORDER BY id").fetchall()
dump("users.json", users)

# 内嵌数据模块:彻底避免运行时 fetch(安卓 WebView 中 fetch 本地 JSON 不可靠)
# 生成 frontend/src/offline/data-embedded.js,data.js 直接 import
def load_json(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as f:
        return json.load(f)

embedded = {
    "textbooks": load_json("textbooks.json"),
    "courses": load_json("courses.json"),
    "vocab_words": load_json("vocab_words.json"),
    "users": [dict(u) for u in users],
}
embed_path = os.path.join("frontend", "src", "offline", "data-embedded.js")
with open(embed_path, "w", encoding="utf-8") as f:
    f.write("// 自动生成:离线内嵌数据(由 scripts/export_offline_data.py 生成,勿手改)\n")
    f.write("export const OFFLINE_DATA = ")
    json.dump(embedded, f, ensure_ascii=False)
    f.write("\n")
print(f"内嵌数据 → {embed_path}, {os.path.getsize(embed_path)//1024} KB")

print("导出完成 →", os.path.abspath(OUT))
