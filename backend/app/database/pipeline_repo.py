"""
AI IMP NEWS OS
Pipeline Stages Repository
Version: 2.0

हर news का पूरा journey tracking:
- Stage 2: IMP Selected
- Stage 3: Verified
- Stage 4: Humanized
- Stage 5: Image + SEO
- Stage 6: Published
- QA: Final Boss approved
"""

from datetime import datetime
from app.database.db import get_connection


class PipelineStagesRepository:
    """Pipeline Journey Tracker"""

    def clear_run(self, run_date):
        """किसी date का पूरा run data delete करो"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pipeline_stages WHERE run_date = ?", (run_date,))
        conn.commit()
        conn.close()

    def create_selected(self, run_date, news_index, title, source="", category="",
                        link="", summary="", image="", raw_score=0, imp_score=0):
        """
        Stage 2: IMP Agent ने जो 6 news select कीं, उन्हें DB में save करो
        """
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            # Delete if exists
            cursor.execute("""
            DELETE FROM pipeline_stages
            WHERE run_date = ? AND news_index = ?
            """, (run_date, news_index))

            cursor.execute("""
            INSERT INTO pipeline_stages(
                run_date, news_index, title, source, category, link, summary, image,
                raw_score, imp_selected, imp_score, stage_reached, created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,1,?,'selected',?,?)
            """, (run_date, news_index, title, source, category, link, summary, image,
                  raw_score, imp_score, now, now))

            conn.commit()
        except Exception as e:
            print(f"[create_selected] Error: {e}")
        finally:
            conn.close()

    def update_verified(self, run_date, news_index, confidence, claims_keywords="",
                        verification_run_id=""):
        """Stage 3: Verification complete"""
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE pipeline_stages
        SET verified = 1,
            confidence = ?,
            claims_keywords = ?,
            verification_run_id = ?,
            stage_reached = 'verified',
            updated_at = ?
        WHERE run_date = ? AND news_index = ?
        """, (confidence, claims_keywords, verification_run_id, now,
              run_date, news_index))

        conn.commit()
        conn.close()

    def update_humanized(self, run_date, news_index, hook="", story="",
                         quality_score=0, decision="", blog_file=""):
        """Stage 4: Humanization complete"""
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE pipeline_stages
        SET hook = ?,
            story = ?,
            quality_score = ?,
            decision = ?,
            blog_file = ?,
            stage_reached = 'humanized',
            updated_at = ?
        WHERE run_date = ? AND news_index = ?
        """, (hook, story, quality_score, decision, blog_file, now,
              run_date, news_index))

        conn.commit()
        conn.close()

    def update_image_seo(self, run_date, news_index, image_prompt="",
                         image_status="pending", image_path="",
                         slug="", meta_title=""):
        """Stage 5: Image + SEO complete"""
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE pipeline_stages
        SET image_prompt = ?,
            image_status = ?,
            image_path = ?,
            slug = ?,
            meta_title = ?,
            stage_reached = 'image_seo',
            updated_at = ?
        WHERE run_date = ? AND news_index = ?
        """, (image_prompt, image_status, image_path, slug, meta_title, now,
              run_date, news_index))

        conn.commit()
        conn.close()

    def update_published(self, run_date, news_index):
        """Stage 6: Publish complete"""
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE pipeline_stages
        SET publish_status = 'published',
            published_at = ?,
            stage_reached = 'published',
            updated_at = ?
        WHERE run_date = ? AND news_index = ?
        """, (now, now, run_date, news_index))

        conn.commit()
        conn.close()

    def update_qa(self, run_date, news_index, approved, notes=""):
        """QA (Final Boss) decision"""
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        stage = "qa_approved" if approved else "qa_rejected"

        cursor.execute("""
        UPDATE pipeline_stages
        SET qa_approved = ?,
            qa_notes = ?,
            stage_reached = ?,
            updated_at = ?
        WHERE run_date = ? AND news_index = ?
        """, (1 if approved else 0, notes, stage, now,
              run_date, news_index))

        conn.commit()
        conn.close()

    def get_journey(self, run_date):
        """किसी date की पूरी journey (सारी 6 news)"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM pipeline_stages
        WHERE run_date = ?
        ORDER BY news_index ASC
        """, (run_date,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_latest_run_date(self):
        """सबसे latest run की date"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT DISTINCT run_date FROM pipeline_stages
        ORDER BY run_date DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        return row["run_date"] if row else None

    def get_all_dates(self, limit=30):
        """Available run dates list"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT DISTINCT run_date FROM pipeline_stages
        ORDER BY run_date DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [row["run_date"] for row in rows]

    def count_by_stage(self, run_date):
        """किसी date के लिए stage-wise count"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(imp_selected) as selected,
            SUM(verified) as verified,
            SUM(CASE WHEN hook IS NOT NULL AND hook != '' THEN 1 ELSE 0 END) as humanized,
            SUM(CASE WHEN image_prompt IS NOT NULL AND image_prompt != '' THEN 1 ELSE 0 END) as with_image,
            SUM(CASE WHEN publish_status = 'published' THEN 1 ELSE 0 END) as published,
            SUM(qa_approved) as qa_approved
        FROM pipeline_stages
        WHERE run_date = ?
        """, (run_date,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {}


if __name__ == "__main__":
    repo = PipelineStagesRepository()

    print("\n🔄 Pipeline Stages Repository Test")
    print("-" * 50)

    latest = repo.get_latest_run_date()
    print(f"Latest Run Date: {latest or 'None'}")

    dates = repo.get_all_dates()
    print(f"All Dates: {len(dates)} runs")

    if latest:
        journey = repo.get_journey(latest)
        print(f"Journey for {latest}: {len(journey)} items")
        counts = repo.count_by_stage(latest)
        print(f"Stage Counts: {counts}")

    print("\n✅ Pipeline Repo working correctly")