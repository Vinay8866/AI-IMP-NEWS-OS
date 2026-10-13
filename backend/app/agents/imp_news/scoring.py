"""
AI IMP NEWS OS
News Scoring Engine
Version: 2.0

हर news को importance score देता है (0-100)।
"""

from app.agents.imp_news.keywords import (
    HIGH_KEYWORDS, MEDIUM_KEYWORDS, LOW_KEYWORDS, NEGATIVE_KEYWORDS
)


def score_article(article):
    """
    Article को score दो।

    Scoring:
    - High keywords   = +10 each (max 50)
    - Medium keywords = +5 each  (max 25)
    - Low keywords    = +2 each  (max 10)
    - Negative        = -5 each
    - Has image       = +5
    - Has summary     = +5
    - Title length OK = +5
    """
    title = (article.get("title") or "").lower()
    summary = (article.get("summary") or "").lower()
    text = f"{title} {summary}"

    score = 0
    matched = []

    # High keywords
    high_hits = 0
    for kw in HIGH_KEYWORDS:
        if kw in text:
            high_hits += 1
            matched.append(kw)
    score += min(high_hits * 10, 50)

    # Medium keywords
    med_hits = 0
    for kw in MEDIUM_KEYWORDS:
        if kw in text:
            med_hits += 1
            matched.append(kw)
    score += min(med_hits * 5, 25)

    # Low keywords
    low_hits = 0
    for kw in LOW_KEYWORDS:
        if kw in text:
            low_hits += 1
    score += min(low_hits * 2, 10)

    # Negative
    for kw in NEGATIVE_KEYWORDS:
        if kw in text:
            score -= 5

    # Bonuses
    if article.get("image"):
        score += 5
    if summary and len(summary) > 50:
        score += 5
    title_len = len(article.get("title") or "")
    if 30 <= title_len <= 120:
        score += 5

    # Clamp 0-100
    score = max(0, min(100, score))

    return score, matched


def score_all(articles):
    """सारी articles को score दो और sort करो (highest first)"""
    scored = []
    for article in articles:
        s, matched = score_article(article)
        article["score"] = s
        article["matched_keywords"] = matched
        scored.append(article)

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


if __name__ == "__main__":
    test = [
        {"title": "OpenAI launches new ChatGPT AI feature", "summary": "Artificial intelligence breakthrough", "image": "x.jpg"},
        {"title": "Local weather update today", "summary": "Rain expected", "image": None},
        {"title": "Google marketing SEO tools for social media", "summary": "New platform for digital marketing campaigns", "image": "y.jpg"},
    ]
    results = score_all(test)
    for r in results:
        print(f"  [{r['score']:3d}] {r['title'][:50]} | keywords: {r['matched_keywords'][:3]}")