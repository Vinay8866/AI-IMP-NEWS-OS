"""
AI IMP NEWS OS
IMP News Selector Agent
Version: 2.0

Stage 2: Database से news लेकर top 6 select करता है।
"""

from app.database.repository import NewsRepository
from app.agents.imp_news.scoring import score_all
from app.config.settings import TOP_NEWS_COUNT


class IMPNewsSelector:
    """Top N News Selector"""

    def __init__(self, top_n=None):
        self.repo = NewsRepository()
        self.top_n = top_n or TOP_NEWS_COUNT

    def top_news(self):
        """
        DB से latest news लो → score करो → top N return करो।
        """
        print("\n" + "=" * 60)
        print("⭐ IMP NEWS SELECTOR - Stage 2")
        print("=" * 60)

        # Get articles from DB
        articles = self.repo.latest(limit=100)
        print(f"📥 Articles from DB: {len(articles)}")

        if not articles:
            print("⚠️  No articles in database. Run News Collector first!")
            print("=" * 60)
            return []

        # Score all
        scored = score_all(articles)

        # Update scores in DB
        for article in scored:
            if article.get("id"):
                self.repo.update_score(article["id"], article["score"])

        # Take top N
        top = scored[:self.top_n]

        print(f"🏆 Top {len(top)} Selected:\n")
        for i, a in enumerate(top, 1):
            print(f"  {i}. [{a['score']:3d}] {a['title'][:55]}")
            print(f"      Source: {a.get('source', 'N/A')} | Category: {a.get('category', 'N/A')}")

        print("=" * 60)
        return top

    def run(self):
        """Agent entry point"""
        return self.top_news()


if __name__ == "__main__":
    selector = IMPNewsSelector()
    top = selector.run()
    print(f"\n🎉 Selected {len(top)} articles for verification")