import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "news.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
print(f"Fixing DB: {DB_PATH}")

cursor.execute("DROP TABLE IF EXISTS pipeline_stages")
cursor.execute("DROP TABLE IF EXISTS selected_articles")
cursor.execute("DROP TABLE IF EXISTS news_articles")
cursor.execute("DROP TABLE IF EXISTS output_articles")

# 1. Raw news
cursor.execute("""
CREATE TABLE news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL,
    summary TEXT,
    published TEXT,
    source TEXT,
    category TEXT,
    hash TEXT UNIQUE,
    image TEXT,
    score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. YE RAHA ASLI TABLE - tere old code ke hisab se pura schema
cursor.execute("""
CREATE TABLE pipeline_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT,
    news_index INTEGER,
    title TEXT,
    source TEXT,
    category TEXT,
    link TEXT,
    summary TEXT,
    image TEXT,
    raw_score INTEGER DEFAULT 0,
    imp_selected INTEGER DEFAULT 0,
    imp_score INTEGER DEFAULT 0,
    stage_reached TEXT DEFAULT 'selected',
    created_at TEXT,
    updated_at TEXT,
    verified INTEGER DEFAULT 0,
    confidence REAL DEFAULT 0,
    claims_keywords TEXT,
    verification_run_id TEXT,
    hook TEXT,
    story TEXT,
    quality_score REAL DEFAULT 0,
    decision TEXT,
    blog_file TEXT,
    image_prompt TEXT,
    image_status TEXT DEFAULT 'pending',
    image_path TEXT,
    slug TEXT,
    meta_title TEXT,
    publish_status TEXT,
    published_at TEXT,
    qa_approved INTEGER DEFAULT 0,
    qa_notes TEXT
);
""")

cursor.execute("""
CREATE TABLE selected_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT,
    news_index INTEGER,
    title TEXT,
    link TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE output_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT,
    title TEXT,
    link TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()
print("✅ DB Fixed FINAL! Ab tere old code ke sare 30 columns ban gaye")