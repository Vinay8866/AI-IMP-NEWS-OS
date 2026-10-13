"""
AI IMP NEWS OS
Database Connection Handler
Version: 2.0

ये file SQLite database को connect करती है।
"""

import sqlite3
from app.config.settings import DB_PATH


def get_connection():
    """
    Database connection return करता है।
    Row factory लगाया है ताकि dict की तरह access कर सकें।
    """
    # Ensure parent directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # ताकि row["column_name"] access कर सकें
    conn.execute("PRAGMA foreign_keys = ON")  # Foreign keys enable
    return conn


def test_connection():
    """Database connection test करता है"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database Connected Successfully")
        print(f"   SQLite Version: {version}")
        print(f"   DB Path: {DB_PATH}")
        return True
    except Exception as e:
        print(f"❌ Database Connection Failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()