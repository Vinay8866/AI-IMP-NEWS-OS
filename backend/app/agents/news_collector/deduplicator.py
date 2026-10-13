"""
AI IMP NEWS OS
News Deduplicator
Version: 2.0

Duplicate news articles हटाता है (hash + title similarity से)।
"""

from difflib import SequenceMatcher


def is_similar(title1, title2, threshold=0.85):
    """
    दो titles कितने similar हैं check करो।
    threshold=0.85 मतलब 85% match = duplicate
    """
    if not title1 or not title2:
        return False
    ratio = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
    return ratio >= threshold


def deduplicate(articles):
    """
    Articles list से duplicates हटाओ।

    Method:
    1. Hash-based exact match
    2. Title similarity match
    """
    if not articles:
        return []

    seen_hashes = set()
    unique = []
    duplicates_count = 0

    for article in articles:
        h = article.get("hash", "")
        title = article.get("title", "")

        # Exact hash match
        if h in seen_hashes:
            duplicates_count += 1
            continue

        # Title similarity check against already kept articles
        is_dup = False
        for kept in unique:
            if is_similar(title, kept.get("title", "")):
                is_dup = True
                duplicates_count += 1
                break

        if not is_dup:
            seen_hashes.add(h)
            unique.append(article)

    print(f"  🔍 Dedup: {len(articles)} → {len(unique)} unique ({duplicates_count} removed)")
    return unique


if __name__ == "__main__":
    # Test
    test_data = [
        {"title": "AI is changing the world", "hash": "aaa", "link": "1"},
        {"title": "AI is changing the world", "hash": "aaa", "link": "1"},  # exact dup
        {"title": "AI is changing the world today", "hash": "bbb", "link": "2"},  # similar
        {"title": "Python 3.14 released", "hash": "ccc", "link": "3"},  # unique
    ]
    result = deduplicate(test_data)
    print(f"Result: {len(result)} unique articles")
    for r in result:
        print(f"  • {r['title']}")