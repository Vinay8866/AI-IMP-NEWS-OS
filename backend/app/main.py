"""
AI IMP NEWS OS
Master Pipeline Orchestrator
Version: 2.0

7-Stage Full Autonomous Pipeline:
Stage 0: Database & Schema Setup
Stage 1: News Collector Agent (RSS)
Stage 2: IMP News Selector Agent (Top 6)
Stage 3: Verify Source Agent (Verification & Evidence)
Stage 4: Human Writer Boss (Hook, Story, Fact, Tone, CTA)
Stage 5: SEO & Image Agent (Slug, Prompts, Media)
Stage 6: Publish Agent (Local Publisher)
Stage 7: Final Boss QA Inspection Agent (Approval Check)
"""

from datetime import datetime

from app.database.schema import create_tables
from app.agents.news_collector.collector import NewsCollectorAgent
from app.agents.verify_source.verify import VerifySourceAgent
from app.agents.human_writer.boss import HumanWriterBoss
from app.agents.publish.publish_agent import PublishAgent
from app.agents.final_boss.qa_agent import FinalBossQAAgent
from app.services.queue_manager.manager import QueueManager


def run_pipeline():
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 70)
    print(f"🚀 AI IMP NEWS OS — MASTER PIPELINE RUN [Started: {today}]")
    print("=" * 70)

    # PHASE 0: Database Setup
    print("\nPHASE 0: DATABASE & SCHEMA SETUP")
    print("-" * 70)
    create_tables()

    # PHASE 1: News Collector Agent (RSS)
    print("\nPHASE 1: NEWS COLLECTOR AGENT")
    print("-" * 70)
    collector = NewsCollectorAgent()
    collector.run()

    # PHASE 2 & 3: Verify Source Agent (Selector + Verification)
    print("\nPHASE 2 & 3: SELECTOR & VERIFY SOURCE AGENT")
    print("-" * 70)
    verifier = VerifySourceAgent()
    verifier.run()

    # PHASE 4 & 5: Human Writer Boss (Content + Image + SEO)
    print("\nPHASE 4 & 5: HUMAN WRITER BOSS (CONTENT + IMAGE + SEO)")
    print("-" * 70)
    writer_boss = HumanWriterBoss()
    writer_results = writer_boss.run()

    # PHASE 6: Queue Manager & Publish Agent
    print("\nPHASE 6: QUEUE MANAGER & PUBLISH AGENT")
    print("-" * 70)
    queue = QueueManager()
    queue.run()

    publisher = PublishAgent()
    publisher.run()

    # PHASE 7: Final Boss QA Inspection
    print("\nPHASE 7: FINAL BOSS / QA INSPECTION AGENT")
    print("-" * 70)
    final_boss = FinalBossQAAgent()
    final_boss.run()

    print("\n" + "=" * 70)
    print(f"🏆 MASTER PIPELINE COMPLETE SUCCESS [Completed: {datetime.now().strftime('%H:%M:%S')}]")
    print("=" * 70 + "\n")

    return writer_results


if __name__ == "__main__":
    run_pipeline()



















    """
AI IMP NEWS OS
Master Pipeline Orchestrator - Buffer Edition
Version: 3.0 - 8 Stages

7-Stage + 8th Buffer Stage:
Stage 0: Database & Schema Setup
Stage 1: News Collector Agent (RSS)
Stage 2: IMP News Selector Agent (Top 6)
Stage 3: Verify Source Agent
Stage 4: Human Writer Boss
Stage 5: SEO & Image Agent
Stage 6: Publish Agent
Stage 7: Final Boss QA
Stage 8: Buffer Clone Social Scheduler (NEW)
"""

from datetime import datetime

from app.database.schema import create_tables
from app.agents.news_collector.collector import NewsCollectorAgent
from app.agents.verify_source.verify import VerifySourceAgent
from app.agents.human_writer.boss import HumanWriterBoss
from app.agents.publish.publish_agent import PublishAgent
from app.agents.final_boss.qa_agent import FinalBossQAAgent
from app.services.queue_manager.manager import QueueManager
from app.config.settings import SOCIAL_ENABLED, SOCIAL_AUTO_SCHEDULE


def run_pipeline():
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 70)
    print(f"🚀 AI IMP NEWS OS — MASTER PIPELINE RUN [Started: {today}]")
    print("=" * 70)

    # PHASE 0: Database Setup
    print("\nPHASE 0: DATABASE & SCHEMA SETUP")
    print("-" * 70)
    create_tables()

    # PHASE 1: News Collector Agent (RSS)
    print("\nPHASE 1: NEWS COLLECTOR AGENT")
    print("-" * 70)
    collector = NewsCollectorAgent()
    collector.run()

    # PHASE 2 & 3: Verify Source Agent
    print("\nPHASE 2 & 3: SELECTOR & VERIFY SOURCE AGENT")
    print("-" * 70)
    verifier = VerifySourceAgent()
    verifier.run()

    # PHASE 4 & 5: Human Writer Boss
    print("\nPHASE 4 & 5: HUMAN WRITER BOSS (CONTENT + IMAGE + SEO)")
    print("-" * 70)
    writer_boss = HumanWriterBoss()
    writer_results = writer_boss.run()

    # PHASE 6: Queue Manager & Publish Agent
    print("\nPHASE 6: QUEUE MANAGER & PUBLISH AGENT")
    print("-" * 70)
    queue = QueueManager()
    queue.run()

    publisher = PublishAgent()
    publisher.run()

    # PHASE 7: Final Boss QA
    print("\nPHASE 7: FINAL BOSS / QA INSPECTION AGENT")
    print("-" * 70)
    final_boss = FinalBossQAAgent()
    final_boss.run()

    # PHASE 8: Buffer Clone Social Scheduler (NEW)
    if SOCIAL_ENABLED and SOCIAL_AUTO_SCHEDULE:
        print("\nPHASE 8: BUFFER CLONE - SOCIAL QUEUE SCHEDULER")
        print("-" * 70)
        try:
            from app.database.repository import OutputRepository
            from app.database.social_repo import SocialScheduleRepository

            output_repo = OutputRepository()
            social_repo = SocialScheduleRepository()

            publish_queue = output_repo.get_publish_queue()
            print(f"📱 Found {len(publish_queue)} articles in Publish Queue for social scheduling")

            scheduled_count = 0
            for article in publish_queue[:6]:  # Top 6 only per run
                # Check if already scheduled for this article
                from app.database.db import get_connection
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as cnt FROM social_schedule WHERE article_id = ?", (article["id"],))
                exists = cursor.fetchone()["cnt"] > 0
                conn.close()

                if not exists:
                    post_id = social_repo.save_from_article(article)
                    if post_id:
                        scheduled_count += 1
                        print(f"  ✅ Scheduled social post ID {post_id} for article: {article['title'][:50]}...")
                else:
                    print(f"  ⏭ Skipped already scheduled: {article['title'][:50]}...")

            print(f"\n📊 Social Scheduling Complete: {scheduled_count} new posts added to Buffer Queue")
            print(f"   Check frontend: content-queue.html -> Social Queue tab")
            print(f"   Or API: GET /api/social/queue")

        except Exception as e:
            print(f"⚠ Social scheduling failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\nPHASE 8: SOCIAL SCHEDULER SKIPPED (SOCIAL_ENABLED=False or SOCIAL_AUTO_SCHEDULE=False)")
        print("-" * 70)

    print("\n" + "=" * 70)
    print(f"🏆 MASTER PIPELINE COMPLETE SUCCESS [Completed: {datetime.now().strftime('%H:%M:%S')}]")
    print("=" * 70 + "\n")

    return writer_results


if __name__ == "__main__":
    run_pipeline()
