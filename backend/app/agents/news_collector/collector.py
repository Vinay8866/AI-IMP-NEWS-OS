"""
AI IMP NEWS OS
News Collector Agent
Version: 2.0

Stage 1: RSS feeds से news collect करके database में save करता है।
"""

from app.agents.news_collector.feeds import get_active_feeds
from app.agents.news_collector.parser import parse_feed
from app.agents.news_collector.deduplicator import deduplicate
from app.database.repository import NewsRepository
from app.config.settings import MAX_RAW_NEWS


class NewsCollectorAgent:
    """RSS News Collector"""

    def __init__(self):
        self.repo = NewsRepository()
        self.feeds = get_active_feeds()

    def collect(self):
        """
        सारे active feeds से news collect करो।
        Returns: list of unique articles
        """
        print("\n" + "=" * 60)
        print("📡 NEWS COLLECTOR AGENT - Stage 1")
        print("=" * 60)
        print(f"Active Feeds: {len(self.feeds)}")
        print("-" * 60)

        all_articles = []

        for feed in self.feeds:
            articles = parse_feed(
                feed_url=feed["url"],
                source_name=feed["name"],
                category=feed["category"]
            )
            all_articles.extend(articles)

        print("-" * 60)
        print(f"📦 Total collected (raw): {len(all_articles)}")

        # Deduplicate
        unique = deduplicate(all_articles)

        # Limit to MAX_RAW_NEWS
        if len(unique) > MAX_RAW_NEWS:
            unique = unique[:MAX_RAW_NEWS]
            print(f"  ✂️  Trimmed to MAX_RAW_NEWS: {MAX_RAW_NEWS}")

        # Save to database
        saved = 0
        skipped = 0
        for article in unique:
            result = self.repo.save(article)
            if result:
                saved += 1
            else:
                skipped += 1  # already exists (INSERT OR IGNORE)

        print("-" * 60)
        print(f"✅ Saved to DB     : {saved} new articles")
        print(f"⏭️  Skipped (dupes) : {skipped}")
        print(f"📊 Total in DB     : {self.repo.count()}")
        print("=" * 60)

        return unique

    def run(self):
        """Agent entry point"""
        return self.collect()


if __name__ == "__main__":
    agent = NewsCollectorAgent()
    articles = agent.run()
    print(f"\n🎉 Collection complete: {len(articles)} articles ready")
    if articles:
        print(f"\nSample headlines:")
        for i, a in enumerate(articles[:5], 1):
            print(f"  {i}. [{a['source']}] {a['title'][:55]}")