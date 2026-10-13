"""
AI IMP NEWS OS
Buffer-style Scheduler Automation
Version: 2.0

रोज़ाना तय समय (सुबह 8:00, दोपहर 4:00, रात 12:00) पर ऑटोमैटिक Pipeline चलाता है।
"""

import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.main import run_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def scheduled_job():
    log.info("=" * 60)
    log.info("⏰ SCHEDULER: Daily Automated Pipeline Job Started")
    log.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 60)

    try:
        run_pipeline()
        log.info("✅ SCHEDULER: Pipeline job completed successfully!")
    except Exception as e:
        log.error(f"❌ SCHEDULER: Pipeline job failed: {e}")


def start_scheduler(hours=[8, 16, 0]):
    scheduler = BlockingScheduler()

    for hour in hours:
        scheduler.add_job(
            scheduled_job,
            trigger=CronTrigger(hour=hour, minute=0),
            id=f"daily_pipeline_{hour:02d}",
            name=f"AI IMP NEWS OS Pipeline at {hour:02d}:00",
            replace_existing=True
        )

    print("\n" + "=" * 70)
    print("⏰ AI IMP NEWS OS — SCHEDULER STARTED")
    print(f"Scheduled Runs: Daily at {hours} Hours")
    print("Press Ctrl+C to stop scheduler.")
    print("=" * 70 + "\n")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[Scheduler Stopped]")
        scheduler.shutdown()


if __name__ == "__main__":
    start_scheduler(hours=[8, 16, 0])