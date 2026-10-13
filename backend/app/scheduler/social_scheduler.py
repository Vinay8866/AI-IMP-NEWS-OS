"""
AI IMP NEWS OS
Buffer Clone Scheduler - Social Media Auto Poster
Version: 3.0

- Pipeline Scheduler (8 AM, 4 PM, 12 AM)
- Social Queue Scheduler (every 2 min check)
"""

import logging
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.main import run_pipeline
from app.database.social_repo import SocialScheduleRepository
from app.services.social.publisher import SocialPublisher
from app.config.settings import SOCIAL_CHECK_INTERVAL_MINUTES, SOCIAL_ENABLED

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def scheduled_pipeline_job():
    log.info("=" * 60)
    log.info("⏰ PIPELINE SCHEDULER: Daily Automated Pipeline Job Started")
    log.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 60)
    try:
        run_pipeline()
        log.info("✅ PIPELINE SCHEDULER: Pipeline job completed!")
    except Exception as e:
        log.error(f"❌ PIPELINE SCHEDULER: Failed: {e}")


def scheduled_social_job():
    """Buffer Clone - Check and post due social posts"""
    if not SOCIAL_ENABLED:
        # Even if disabled, we still process mock posts
        pass

    log.info(f"📱 SOCIAL SCHEDULER: Checking due posts at {datetime.now().strftime('%H:%M:%S')}")
    try:
        repo = SocialScheduleRepository()
        due_posts = repo.get_due_posts()

        if not due_posts:
            log.info("📭 No due social posts")
            return

        log.info(f"📬 Found {len(due_posts)} due posts to publish")
        publisher = SocialPublisher()

        for post in due_posts:
            log.info(f"🚀 Publishing social post ID {post['id']}: {post['title'][:50]}...")
            try:
                result = publisher.publish(post)
                if result.get("success"):
                    fb_id = result.get("results", {}).get("facebook")
                    ig_id = result.get("results", {}).get("instagram")
                    # For mock mode, fb_id is mock_xxx
                    status = "simulated" if result.get("mode") == "mock" else "posted"
                    repo.update_status(
                        post["id"],
                        status,
                        fb_post_id=str(fb_id) if fb_id else None,
                        ig_post_id=str(ig_id) if ig_id else None
                    )
                    log.info(f"✅ Posted ID {post['id']} -> FB: {fb_id}, IG: {ig_id} (mode: {result.get('mode')})")
                else:
                    repo.update_status(post["id"], "failed", error=result.get("error", "Unknown error"))
                    log.error(f"❌ Failed ID {post['id']}: {result.get('error')}")
            except Exception as e:
                repo.update_status(post["id"], "failed", error=str(e))
                log.error(f"❌ Exception publishing ID {post['id']}: {e}")

    except Exception as e:
        log.error(f"❌ SOCIAL SCHEDULER: Failed: {e}")


def start_combined_scheduler(pipeline_hours=[8, 16, 0]):
    """Dono schedulers ek saath - Background Scheduler"""
    scheduler = BackgroundScheduler()

    # Pipeline jobs
    for hour in pipeline_hours:
        scheduler.add_job(
            scheduled_pipeline_job,
            trigger=CronTrigger(hour=hour, minute=0),
            id=f"daily_pipeline_{hour:02d}",
            name=f"AI IMP NEWS OS Pipeline at {hour:02d}:00",
            replace_existing=True
        )

    # Social queue checker - every 2 minutes
    scheduler.add_job(
        scheduled_social_job,
        trigger=IntervalTrigger(minutes=SOCIAL_CHECK_INTERVAL_MINUTES),
        id="social_queue_checker",
        name=f"Buffer Clone Social Queue Checker (every {SOCIAL_CHECK_INTERVAL_MINUTES} min)",
        replace_existing=True
    )

    print("\n" + "=" * 70)
    print("⏰ AI IMP NEWS OS — COMBINED SCHEDULER STARTED (Buffer Edition)")
    print(f"Pipeline Runs: Daily at {pipeline_hours} Hours")
    print(f"Social Queue: Every {SOCIAL_CHECK_INTERVAL_MINUTES} minutes")
    print(f"Social Mode: {'Mock' if not SocialPublisher().is_real_mode() else 'Real FB/IG'}")
    print("Press Ctrl+C to stop scheduler.")
    print("=" * 70 + "\n")

    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Scheduler Stopped]")
        scheduler.shutdown()


def start_blocking_scheduler(hours=[8, 16, 0]):
    """Old Blocking version - only pipeline"""
    scheduler = BlockingScheduler()
    for hour in hours:
        scheduler.add_job(
            scheduled_pipeline_job,
            trigger=CronTrigger(hour=hour, minute=0),
            id=f"daily_pipeline_{hour:02d}",
            name=f"AI IMP NEWS OS Pipeline at {hour:02d}:00",
            replace_existing=True
        )
    print("\n" + "=" * 70)
    print("⏰ AI IMP NEWS OS — SCHEDULER STARTED (Blocking - Pipeline Only)")
    print(f"Scheduled Runs: Daily at {hours} Hours")
    print("=" * 70 + "\n")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[Scheduler Stopped]")
        scheduler.shutdown()


if __name__ == "__main__":
    # Combined scheduler - both pipeline + social
    start_combined_scheduler(pipeline_hours=[8, 16, 0])
