"""
AI IMP NEWS OS
News & Output Repository
Version: 2.0

2 Classes:
- NewsRepository: Raw news articles को handle करता है (Stage 1)
- OutputRepository: Final output को handle करता है (Final content)
"""

from app.database.db import get_connection


class NewsRepository:
    """Raw News articles के लिए (Stage 1)"""

    def save(self, article):
        """
        Article save करो। Duplicate detect करने के लिए hash use होता है।

        article dict में ये keys होनी चाहिए:
        - title, link, summary, published, source, category, hash
        - image (optional), score (optional)
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT OR IGNORE INTO news_articles(
                title, link, summary, published, source, category, hash, image, score
            )
            VALUES(?,?,?,?,?,?,?,?,?)
            """, (
                article.get("title", ""),
                article.get("link", ""),
                article.get("summary", ""),
                article.get("published", ""),
                article.get("source", ""),
                article.get("category", ""),
                article.get("hash", ""),
                article.get("image"),
                article.get("score", 0)
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[NewsRepository.save] Error: {e}")
            return None
        finally:
            conn.close()

    def latest(self, limit=50):
        """Latest news return करो (score के हिसाब से)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM news_articles
        ORDER BY score DESC, created_at DESC
        LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def count(self):
        """Total count"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM news_articles")
        row = cursor.fetchone()
        conn.close()
        return row["cnt"] if row else 0

    def get_by_hash(self, hash_val):
        """Hash से article ढूंढो (duplicate check के लिए)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM news_articles WHERE hash = ?", (hash_val,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_score(self, article_id, score):
        """किसी article का score update करो"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE news_articles SET score = ? WHERE id = ?",
                       (score, article_id))
        conn.commit()
        conn.close()

    def clear_old(self, days=7):
        """Purani news delete करो (days से ज्यादा पुरानी)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM news_articles
        WHERE created_at < datetime('now', '-' || ? || ' days')
        """, (days,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted


class OutputRepository:
    """Final Output के लिए (Publish Queue, Rewrite Queue)"""

    def save(self, run_date, news_index, result, seo_data=None):
        """
        Humanized output save करो।

        result dict में ये keys होनी चाहिए:
        - title, hook, confidence, quality, decision, file
        - source, category
        """
        conn = get_connection()
        cursor = conn.cursor()

        slug = ""
        meta_title = ""
        if seo_data:
            slug = seo_data.get("slug", "")
            meta_title = seo_data.get("meta_title", "")

        try:
            # Delete existing (duplicate protection)
            cursor.execute("""
            DELETE FROM articles_output
            WHERE run_date = ? AND news_index = ?
            """, (run_date, news_index))

            # Insert new
            cursor.execute("""
            INSERT INTO articles_output(
                run_date, news_index, title, hook, confidence, quality_score,
                decision, file_path, slug, meta_title, source, category, publish_status
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                run_date, news_index,
                result.get("title", ""),
                result.get("hook", ""),
                result.get("confidence", 0),
                result.get("quality", 0),
                result.get("decision", "REWRITE_QUEUE"),
                result.get("file", ""),
                slug, meta_title,
                result.get("source", ""),
                result.get("category", ""),
                "pending"
            ))
            conn.commit()
        except Exception as e:
            print(f"[OutputRepository.save] Error: {e}")
        finally:
            conn.close()

    def get_publish_queue(self):
        """Publish-ready articles"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM articles_output
        WHERE decision = 'PUBLISH_QUEUE' AND publish_status = 'pending'
        ORDER BY created_at ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_rewrite_queue(self):
        """Rewrite-needed articles"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM articles_output
        WHERE decision = 'REWRITE_QUEUE' AND publish_status = 'pending'
        ORDER BY created_at ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_published(self, article_id):
        """Article को published mark करो"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE articles_output
        SET publish_status = 'published'
        WHERE id = ?
        """, (article_id,))
        conn.commit()
        conn.close()

    def today_summary(self, run_date):
        """किसी date का summary"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN decision = 'PUBLISH_QUEUE' THEN 1 ELSE 0 END) as publish_count,
            SUM(CASE WHEN decision = 'REWRITE_QUEUE' THEN 1 ELSE 0 END) as rewrite_count,
            AVG(quality_score) as avg_quality,
            AVG(confidence) as avg_confidence
        FROM articles_output
        WHERE run_date = ?
        """, (run_date,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}

    def get_published_count(self, run_date):
        """Published count for a date"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT COUNT(*) as count
        FROM articles_output
        WHERE run_date = ? AND publish_status = 'published'
        """, (run_date,))
        row = cursor.fetchone()
        conn.close()
        return row["count"] if row else 0

    def get_all_runs(self, days=30):
        """Last N days के सारे runs"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
            run_date,
            COUNT(*) as total,
            SUM(CASE WHEN decision = 'PUBLISH_QUEUE' THEN 1 ELSE 0 END) as publish_count,
            SUM(CASE WHEN decision = 'REWRITE_QUEUE' THEN 1 ELSE 0 END) as rewrite_count,
            AVG(quality_score) as avg_quality,
            AVG(confidence) as avg_confidence
        FROM articles_output
        WHERE run_date >= date('now', '-' || ? || ' days')
        GROUP BY run_date
        ORDER BY run_date DESC
        """, (days,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]


if __name__ == "__main__":
    # Quick test
    news_repo = NewsRepository()
    output_repo = OutputRepository()

    print(f"\n📰 Total News Articles: {news_repo.count()}")

    latest = news_repo.latest(5)
    print(f"📋 Latest 5 Articles: {len(latest)} found")

    pub_queue = output_repo.get_publish_queue()
    print(f"📤 Publish Queue: {len(pub_queue)} items")

    rew_queue = output_repo.get_rewrite_queue()
    print(f"✏️  Rewrite Queue: {len(rew_queue)} items")

    print("\n✅ Repository working correctly")