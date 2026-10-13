"""
AI IMP NEWS OS
Queue Manager Service
Version: 2.0

Publish Queue और Rewrite Queue का प्रबंधन करता है।
"""

from app.database.repository import OutputRepository


class QueueManager:
    """Queue Processing Manager"""

    def __init__(self):
        self.db = OutputRepository()

    def get_publish_queue(self):
        """Publish-ready articles प्राप्त करें"""
        return self.db.get_publish_queue()

    def get_rewrite_queue(self):
        """Rewrite-needed articles प्राप्त करें"""
        return self.db.get_rewrite_queue()

    def process_publish_queue(self):
        """Publish queue की जांच और प्रिंटिंग"""
        queue = self.get_publish_queue()
        print(f"\n📤 PUBLISH QUEUE: {len(queue)} articles pending")
        for item in queue:
            print(f"  • [ID {item['id']}] Q={item['quality_score']}/100 | {item['title'][:55]}...")
        return queue

    def process_rewrite_queue(self):
        """Rewrite queue की जांच और प्रिंटिंग"""
        queue = self.get_rewrite_queue()
        print(f"\n✏️  REWRITE QUEUE: {len(queue)} articles pending")
        for item in queue:
            print(f"  • [ID {item['id']}] Q={item['quality_score']}/100 | {item['title'][:55]}...")
        return queue

    def mark_as_published(self, article_id):
        """Article को published के रूप में मार्क करें"""
        self.db.mark_published(article_id)
        print(f"✅ Article ID {article_id} marked as PUBLISHED")

    def run(self):
        """Queue Manager Entry Point"""
        print("\n" + "=" * 60)
        print("🚦 QUEUE MANAGER SERVICE")
        print("=" * 60)

        pub_items = self.process_publish_queue()
        rew_items = self.process_rewrite_queue()

        print("-" * 60)
        print(f"📊 Summary: {len(pub_items)} Ready to Publish | {len(rew_items)} Needs Rewrite")
        print("=" * 60)

        return {
            "publish_queue": pub_items,
            "rewrite_queue": rew_items
        }


if __name__ == "__main__":
    manager = QueueManager()
    manager.run()