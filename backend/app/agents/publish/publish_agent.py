"""
AI IMP NEWS OS
Publish Agent (Local Mode)
Version: 2.0

Stage 6:
- Publish Queue से आर्टिकल्स लेता है
- Docs/Published फोल्डर में ट्रांसफर करता है
- DB में status update करता है
"""

import shutil
from pathlib import Path
from datetime import datetime

from app.database.repository import OutputRepository
from app.database.pipeline_repo import PipelineStagesRepository
from app.config.settings import PUBLISHED_DIR


class PublishAgent:
    """Local File Publisher Agent"""

    def __init__(self):
        self.output_repo = OutputRepository()
        self.stages_repo = PipelineStagesRepository()
        PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)

    def publish_one(self, item):
        """एक आर्टिकल पब्लिश करें"""
        file_path_str = item.get("file_path", "")
        if not file_path_str:
            print(f"  ❌ Missing file path for ID {item['id']}")
            return False

        source_file = Path(file_path_str)
        if not source_file.exists():
            print(f"  ❌ File missing on disk for ID {item['id']}: {source_file}")
            return False

        source_folder = source_file.parent
        run_date = item["run_date"]
        news_index = item["news_index"]

        # Destination: docs/published/2026-10-07/news_001
        dest_folder = PUBLISHED_DIR / run_date / f"news_{news_index:03d}"

        if dest_folder.exists():
            shutil.rmtree(dest_folder)

        # Copy complete folder (blog.md, seo.json, meta.json, etc.)
        shutil.copytree(source_folder, dest_folder)

        # Update DBs
        self.output_repo.mark_published(item["id"])
        self.stages_repo.update_published(run_date, news_index)

        print(f"  ✅ Published ID #{item['id']} (News_{news_index:03d})")
        print(f"     → {dest_folder}")
        return True

    def run(self):
        """Publish Agent Entry Point"""
        print("\n" + "=" * 60)
        print("🚀 PUBLISH AGENT (LOCAL MODE) - Stage 6")
        print("=" * 60)

        queue = self.output_repo.get_publish_queue()

        if not queue:
            print("ℹ️  No articles in PUBLISH_QUEUE pending publish.")
            print("=" * 60)
            return {"published": 0, "failed": 0}

        print(f"Found {len(queue)} article(s) ready to publish:\n")

        published_count = 0
        failed_count = 0

        for item in queue:
            success = self.publish_one(item)
            if success:
                published_count += 1
            else:
                failed_count += 1

        print("-" * 60)
        print(f"🎉 PUBLISH COMPLETE: {published_count} Published | {failed_count} Failed")
        print("=" * 60)

        return {
            "published": published_count,
            "failed": failed_count
        }


if __name__ == "__main__":
    agent = PublishAgent()
    agent.run()