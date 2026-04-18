"""Migrate database from old schema to new textbook-based schema."""
import shutil, os, sqlite3
from datetime import datetime

DB_PATH = "data/english_learning.db"
BACKUP_PATH = f"data/english_learning.db.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"

print("=== Database Migration ===")

# Step 1: Backup
if os.path.exists(DB_PATH):
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"Backup created: {BACKUP_PATH}")
else:
    print("No existing database found, will create new one.")

# Step 2: Drop old tables
if os.path.exists(DB_PATH):
    c = sqlite3.connect(DB_PATH)
    # Get all existing tables
    cur = c.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing = [row[0] for row in cur.fetchall()]

    # Drop tables in reverse FK order
    drop_order = [
        "unit_progress", "daily_progress", "scores",
        "questions", "units", "courses",
        "vocab_words", "textbooks",
    ]
    for table in drop_order:
        if table in existing:
            cur.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  Dropped table: {table}")
    c.commit()
    c.close()

# Step 3: Create new tables
from app.database import engine, Base, SessionLocal
from app.models import Textbook, Unit

Base.metadata.create_all(bind=engine)
print("New tables created.")

# Step 4: Create textbooks and units
db = SessionLocal()

# Big Muzzy textbook
muzzy = Textbook(
    name="Big Muzzy 玛泽的故事",
    source_path="/mnt/f/1.英语启蒙/Big Muzzy 玛泽的故事",
    cover_image="",
)
db.add(muzzy)
db.commit()
db.refresh(muzzy)

for i in range(1, 13):
    db.add(Unit(textbook_id=muzzy.id, name=f"第{i}集", order=i))
db.commit()
print(f"Big Muzzy: textbook id={muzzy.id}, 12 units created")

# Oxford Phonics textbook
phonics = Textbook(
    name="Oxford Phonics World 牛津自然拼读",
    source_path="/mnt/f/1.英语启蒙/牛津自然拼读世界全套视频+电子书",
    cover_image="",
)
db.add(phonics)
db.commit()
db.refresh(phonics)

for level in range(1, 6):
    db.add(Unit(textbook_id=phonics.id, name=f"Level {level}", order=level))
db.commit()
print(f"Oxford Phonics: textbook id={phonics.id}, 5 units created")

# Verify
import sqlite3
c = sqlite3.connect(DB_PATH)
cur = c.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(f"\nTables: {[r[0] for r in cur.fetchall()]}")
cur.execute("SELECT COUNT(*) FROM textbooks")
print(f"Textbooks: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM units")
print(f"Units: {cur.fetchone()[0]}")
c.close()

db.close()
print("Migration complete!")
