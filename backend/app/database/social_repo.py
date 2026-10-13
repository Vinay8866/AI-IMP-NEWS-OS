"""
AI IMP NEWS OS
Social Schedule Repository - Buffer Clone Core
Version: 3.0
Handles Buffer-style Queue: queued -> scheduled -> posted -> failed
"""

import json
from datetime import datetime, timedelta
from app.database.db import get_connection


class SocialScheduleRepository:
    """Buffer Clone Queue Manager"""

    def save_from_article(self, article_output_row, caption=None, platforms=None, scheduled_at=None):
        """
        articles_output row se social post banao
        article_output_row = dict from OutputRepository.get_publish_queue()
        """
        conn = get_connection()
        cursor = conn.cursor()

        # Generate caption if not provided
        if not caption:
            caption = self.generate_caption(article_output_row)

        if platforms is None:
            from app.config.settings import SOCIAL_DEFAULT_PLATFORMS
            platforms = SOCIAL_DEFAULT_PLATFORMS

        # Default scheduled_at = next optimal slot
        if not scheduled_at:
            scheduled_at = self.get_next_buffer_slot()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "scheduled" if scheduled_at else "queued"

        try:
            cursor.execute("""
            INSERT INTO social_schedule(
                run_date, news_index, article_id, title, hook, caption,
                image_path, link, source, category,
                platforms, scheduled_at, status, buffer_slot,
                created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                article_output_row.get("run_date", ""),
                article_output_row.get("news_index", 0),
                article_output_row.get("id"),
                article_output_row.get("title", ""),
                article_output_row.get("hook", ""),
                caption,
                article_output_row.get("image_path") or "",
                article_output_row.get("link", ""),
                article_output_row.get("source", ""),
                article_output_row.get("category", ""),
                json.dumps(platforms),
                scheduled_at,
                status,
                self.get_slot_label(scheduled_at) if scheduled_at else "queued",
                now, now
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[SocialRepo.save_from_article] Error: {e}")
            return None
        finally:
            conn.close()

    def generate_caption(self, article):
        """Hook + Title se Buffer style caption banao"""
        title = article.get("title", "")
        hook = article.get("hook", "")
        category = article.get("category", "")
        source = article.get("source", "")

        # Buffer style: Hook + Emoji + Title + Hashtags
        hashtags = self.generate_hashtags(category, title)

        caption = f"{hook}\n\n📰 {title}\n\n"
        caption += f"{hashtags}\n"
        if source:
            caption += f"\nvia {source} | #AIIMPNews"

        # Limit for Instagram (2200) but keep short
        if len(caption) > 500:
            caption = caption[:480] + "..."

        return caption.strip()

    def generate_hashtags(self, category, title):
        from app.config.settings import SOCIAL_CAPTION_HASHTAGS
        base = ["#BreakingNews", "#NewsUpdate", "#IndiaNews"]
        if category:
            base.append(f"#{category.replace(' ', '').replace('-','')}")
        # Extract keywords from title
        keywords = [w for w in title.split() if len(w) > 4][:2]
        for kw in keywords:
            clean = "".join(c for c in kw if c.isalnum())
            if clean:
                base.append(f"#{clean}")

        return " ".join(base[:SOCIAL_CAPTION_HASHTAGS + 2])

    def get_next_buffer_slot(self):
        """Next optimal Buffer slot nikal (08:00, 13:00, 19:00)"""
        from app.config.settings import SOCIAL_POST_TIMES
        now = datetime.now()

        # Try today slots
        for t_str in SOCIAL_POST_TIMES:
            try:
                h, m = map(int, t_str.split(":"))
                slot = now.replace(hour=h, minute=m, second=0, microsecond=0)
                if slot > now + timedelta(minutes=5):  # at least 5 min in future
                    # Check if slot free?
                    if not self.is_slot_taken(slot):
                        return slot.strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue

        # Tomorrow first slot
        tomorrow = now + timedelta(days=1)
        try:
            h, m = map(int, SOCIAL_POST_TIMES[0].split(":"))
            slot = tomorrow.replace(hour=h, minute=m, second=0, microsecond=0)
            return slot.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

    def is_slot_taken(self, dt):
        """Check if already a post scheduled at same hour"""
        conn = get_connection()
        cursor = conn.cursor()
        dt_str = dt.strftime("%Y-%m-%d %H:%M")
        cursor.execute("""
        SELECT COUNT(*) as cnt FROM social_schedule
        WHERE status = 'scheduled' AND scheduled_at LIKE ?
        """, (f"{dt_str}%",))
        row = cursor.fetchone()
        conn.close()
        return (row["cnt"] if row else 0) > 0

    def get_slot_label(self, scheduled_at_str):
        try:
            dt = datetime.strptime(scheduled_at_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%I:%M %p - %d %b")
        except:
            return scheduled_at_str

    def get_queue(self, status=None, limit=50):
        """Queue fetch - Buffer style"""
        conn = get_connection()
        cursor = conn.cursor()
        if status:
            cursor.execute("""
            SELECT * FROM social_schedule
            WHERE status = ?
            ORDER BY scheduled_at ASC, created_at ASC
            LIMIT ?
            """, (status, limit))
        else:
            cursor.execute("""
            SELECT * FROM social_schedule
            ORDER BY 
                CASE status
                    WHEN 'scheduled' THEN 1
                    WHEN 'queued' THEN 2
                    WHEN 'posted' THEN 3
                    WHEN 'failed' THEN 4
                    ELSE 5
                END,
                scheduled_at ASC
            LIMIT ?
            """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_due_posts(self):
        """Jo posts ab post hone chahiye (scheduled_at <= now)"""
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        SELECT * FROM social_schedule
        WHERE status = 'scheduled' AND scheduled_at <= ?
        ORDER BY scheduled_at ASC
        """, (now,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_status(self, post_id, status, fb_post_id=None, ig_post_id=None, error=None):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            if status == "posted":
                cursor.execute("""
                UPDATE social_schedule
                SET status = ?, posted_at = ?, fb_post_id = COALESCE(?, fb_post_id),
                    ig_post_id = COALESCE(?, ig_post_id), error_message = NULL, updated_at = ?
                WHERE id = ?
                """, (status, now, fb_post_id, ig_post_id, now, post_id))
            elif status == "failed":
                cursor.execute("""
                UPDATE social_schedule
                SET status = ?, error_message = ?, retry_count = retry_count + 1, updated_at = ?
                WHERE id = ?
                """, (status, error, now, post_id))
            else:
                cursor.execute("""
                UPDATE social_schedule
                SET status = ?, updated_at = ?
                WHERE id = ?
                """, (status, now, post_id))
            conn.commit()
        finally:
            conn.close()

    def reschedule(self, post_id, new_scheduled_at):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        UPDATE social_schedule
        SET scheduled_at = ?, status = 'scheduled', buffer_slot = ?, updated_at = ?
        WHERE id = ?
        """, (new_scheduled_at, self.get_slot_label(new_scheduled_at), now, post_id))
        conn.commit()
        conn.close()

    def update_caption(self, post_id, new_caption, platforms=None):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if platforms:
            cursor.execute("""
            UPDATE social_schedule
            SET caption = ?, platforms = ?, updated_at = ?
            WHERE id = ?
            """, (new_caption, json.dumps(platforms), now, post_id))
        else:
            cursor.execute("""
            UPDATE social_schedule
            SET caption = ?, updated_at = ?
            WHERE id = ?
            """, (new_caption, now, post_id))
        conn.commit()
        conn.close()

    def delete(self, post_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM social_schedule WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()

    def count_by_status(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT status, COUNT(*) as cnt FROM social_schedule
        GROUP BY status
        """)
        rows = cursor.fetchall()
        conn.close()
        result = {r["status"]: r["cnt"] for r in rows}
        return {
            "queued": result.get("queued", 0),
            "scheduled": result.get("scheduled", 0),
            "posted": result.get("posted", 0),
            "failed": result.get("failed", 0),
            "total": sum(result.values())
        }

    def get_calendar(self, days=7):
        """Next 7 days ka calendar view"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM social_schedule
        WHERE scheduled_at >= datetime('now', '-1 day')
        AND scheduled_at <= datetime('now', '+' || ? || ' days')
        ORDER BY scheduled_at ASC
        """, (days,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
