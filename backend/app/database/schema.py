"""
AI IMP NEWS OS
Database Schema (All Tables)
Version: 2.0

4 Tables:
1. news_articles       - RSS से इकट्ठा हुई raw news
2. articles_output     - Final content (publish queue)
3. pipeline_analytics  - Analytics tracking
4. pipeline_stages     - हर news की full journey (6 stages)
"""

from app.database.db import get_connection


def create_tables():
    """सारी tables बनाओ अगर नहीं हैं"""

    conn = get_connection()
    cursor = conn.cursor()

    # ===== Table 1: news_articles (Stage 1 - Raw News) =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news_articles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        link TEXT UNIQUE,
        summary TEXT,
        published TEXT,
        source TEXT,
        category TEXT,
        hash TEXT UNIQUE,
        image TEXT,
        score INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ===== Table 2: articles_output (Final Content) =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles_output(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT NOT NULL,
        news_index INTEGER NOT NULL,
        title TEXT NOT NULL,
        hook TEXT,
        confidence INTEGER DEFAULT 0,
        quality_score INTEGER DEFAULT 0,
        decision TEXT,
        file_path TEXT,
        slug TEXT,
        meta_title TEXT,
        source TEXT,
        category TEXT,
        publish_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ===== Table 3: pipeline_analytics =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_analytics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT NOT NULL,
        stage TEXT NOT NULL,
        agent_name TEXT,
        status TEXT DEFAULT 'pending',
        started_at TEXT,
        completed_at TEXT,
        duration_seconds REAL DEFAULT 0,
        input_count INTEGER DEFAULT 0,
        output_count INTEGER DEFAULT 0,
        error_message TEXT,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ===== Table 4: pipeline_stages (Full Journey Tracking) =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_stages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT NOT NULL,
        news_index INTEGER NOT NULL,

        -- Basic Info (from Raw News)
        title TEXT,
        source TEXT,
        category TEXT,
        link TEXT,
        summary TEXT,
        image TEXT,
        raw_score INTEGER DEFAULT 0,

        -- Stage 2: IMP Selection
        imp_selected INTEGER DEFAULT 0,
        imp_score REAL DEFAULT 0,

        -- Stage 3: Verification
        verified INTEGER DEFAULT 0,
        confidence REAL DEFAULT 0,
        claims_keywords TEXT,
        verification_run_id TEXT,

        -- Stage 4: Humanization
        hook TEXT,
        story TEXT,
        quality_score INTEGER DEFAULT 0,
        decision TEXT,
        blog_file TEXT,

        -- Stage 5: Image + SEO
        image_prompt TEXT,
        image_status TEXT DEFAULT 'pending',
        image_path TEXT,
        slug TEXT,
        meta_title TEXT,

        -- Stage 6: Publish
        publish_status TEXT DEFAULT 'pending',
        published_at TEXT,

        -- QA (Final Boss)
        qa_approved INTEGER DEFAULT 0,
        qa_notes TEXT,

        -- Tracking
        stage_reached TEXT DEFAULT 'selected',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        UNIQUE(run_date, news_index)
    )
    """)

    # ===== Indexes for faster queries =====
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_source ON news_articles(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_output_rundate ON articles_output(run_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stages_rundate ON pipeline_stages(run_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_rundate ON pipeline_analytics(run_date)")

    conn.commit()
    conn.close()

    print("✅ All 4 tables created/verified successfully")


def drop_all_tables():
    """सारी tables delete करो (DANGER - सावधानी से use करें)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS news_articles")
    cursor.execute("DROP TABLE IF EXISTS articles_output")
    cursor.execute("DROP TABLE IF EXISTS pipeline_analytics")
    cursor.execute("DROP TABLE IF EXISTS pipeline_stages")
    conn.commit()
    conn.close()
    print("⚠️  All tables dropped")


def show_tables():
    """मौजूदा tables दिखाओ"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()

    print("\n📋 Tables in Database:")
    print("-" * 40)
    for table in tables:
        print(f"   • {table['name']}")
    print("-" * 40)
    return [t["name"] for t in tables]


if __name__ == "__main__":
    print("Creating database schema...")
    create_tables()
    show_tables()



















    """
AI IMP NEWS OS
Database Schema (All Tables)
Version: 3.0 Buffer Edition

5 Tables:
1. news_articles       - RSS raw news
2. articles_output     - Final content (publish queue)
3. pipeline_analytics  - Analytics tracking
4. pipeline_stages     - Full journey (6 stages)
5. social_schedule     - NEW Buffer Clone Queue & Scheduler
"""

from app.database.db import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: news_articles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news_articles(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        link TEXT UNIQUE,
        summary TEXT,
        published TEXT,
        source TEXT,
        category TEXT,
        hash TEXT UNIQUE,
        image TEXT,
        score INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Table 2: articles_output
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles_output(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT NOT NULL,
        news_index INTEGER NOT NULL,
        title TEXT NOT NULL,
        hook TEXT,
        confidence INTEGER DEFAULT 0,
        quality_score INTEGER DEFAULT 0,
        decision TEXT,
        file_path TEXT,
        slug TEXT,
        meta_title TEXT,
        source TEXT,
        category TEXT,
        publish_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Table 3: pipeline_analytics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_analytics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT NOT NULL,
        stage TEXT NOT NULL,
        agent_name TEXT,
        status TEXT DEFAULT 'pending',
        started_at TEXT,
        completed_at TEXT,
        duration_seconds REAL DEFAULT 0,
        input_count INTEGER DEFAULT 0,
        output_count INTEGER DEFAULT 0,
        error_message TEXT,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Table 4: pipeline_stages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_stages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT NOT NULL,
        news_index INTEGER NOT NULL,
        title TEXT,
        source TEXT,
        category TEXT,
        link TEXT,
        summary TEXT,
        image TEXT,
        raw_score INTEGER DEFAULT 0,
        imp_selected INTEGER DEFAULT 0,
        imp_score REAL DEFAULT 0,
        verified INTEGER DEFAULT 0,
        confidence REAL DEFAULT 0,
        claims_keywords TEXT,
        verification_run_id TEXT,
        hook TEXT,
        story TEXT,
        quality_score INTEGER DEFAULT 0,
        decision TEXT,
        blog_file TEXT,
        image_prompt TEXT,
        image_status TEXT DEFAULT 'pending',
        image_path TEXT,
        slug TEXT,
        meta_title TEXT,
        publish_status TEXT DEFAULT 'pending',
        published_at TEXT,
        qa_approved INTEGER DEFAULT 0,
        qa_notes TEXT,
        stage_reached TEXT DEFAULT 'selected',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(run_date, news_index)
    )
    """)

    # ===== Table 5: social_schedule (BUFFER CLONE - NEW) =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS social_schedule(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date TEXT NOT NULL,
        news_index INTEGER NOT NULL,
        article_id INTEGER,
        title TEXT NOT NULL,
        hook TEXT,
        caption TEXT NOT NULL,
        image_path TEXT,
        image_url TEXT,
        link TEXT,
        source TEXT,
        category TEXT,
        platforms TEXT NOT NULL DEFAULT '["facebook"]',
        scheduled_at TEXT,
        status TEXT NOT NULL DEFAULT 'queued',
        buffer_slot TEXT,
        posted_at TEXT,
        fb_post_id TEXT,
        ig_post_id TEXT,
        error_message TEXT,
        retry_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(article_id) REFERENCES articles_output(id) ON DELETE SET NULL
    )
    """)

    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_source ON news_articles(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_output_rundate ON articles_output(run_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stages_rundate ON pipeline_stages(run_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_rundate ON pipeline_analytics(run_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_social_rundate ON social_schedule(run_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_social_status ON social_schedule(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_social_scheduled_at ON social_schedule(scheduled_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_social_article ON social_schedule(article_id)")

    conn.commit()
    conn.close()
    print("✅ All 5 tables created/verified (including social_schedule - Buffer Clone)")


def drop_all_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS social_schedule")
    cursor.execute("DROP TABLE IF EXISTS news_articles")
    cursor.execute("DROP TABLE IF EXISTS articles_output")
    cursor.execute("DROP TABLE IF EXISTS pipeline_analytics")
    cursor.execute("DROP TABLE IF EXISTS pipeline_stages")
    conn.commit()
    conn.close()
    print("⚠ All tables dropped")


def show_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()
    print("\n📋 Tables:")
    print("-" * 40)
    for table in tables:
        print(f"   • {table['name']}")
    print("-" * 40)
    return [t["name"] for t in tables]


if __name__ == "__main__":
    create_tables()
    show_tables()
