"""
AI IMP NEWS OS
IMP News Keywords
Version: 2.0

Keywords जिनके आधार पर news की importance score होती है।
"""

# High importance keywords (score +10 each)
HIGH_KEYWORDS = [
    "ai", "artificial intelligence", "chatgpt", "openai", "google",
    "microsoft", "apple", "amazon", "meta", "nvidia",
    "launch", "release", "breakthrough", "revolution",
    "funding", "ipo", "acquisition", "merger",
    "marketing", "seo", "social media", "viral",
    "algorithm", "machine learning", "deep learning",
    "startup", "innovation", "disruption",
]

# Medium importance keywords (score +5 each)
MEDIUM_KEYWORDS = [
    "update", "feature", "tool", "platform", "app",
    "growth", "strategy", "campaign", "content",
    "analytics", "data", "automation", "productivity",
    "cloud", "saas", "api", "integration",
    "instagram", "tiktok", "youtube", "linkedin", "twitter",
    "facebook", "whatsapp", "threads",
    "ecommerce", "retail", "brand", "advertising",
]

# Low / context keywords (score +2 each)
LOW_KEYWORDS = [
    "new", "best", "top", "guide", "how to",
    "tips", "trends", "report", "study", "research",
    "free", "open source", "beta", "preview",
]

# Negative keywords (score -5 each) — low quality signals
NEGATIVE_KEYWORDS = [
    "sponsored", "advertisement", "coupon", "deal",
    "casino", "crypto scam", "click here",
]


def get_all_keywords():
    return {
        "high": HIGH_KEYWORDS,
        "medium": MEDIUM_KEYWORDS,
        "low": LOW_KEYWORDS,
        "negative": NEGATIVE_KEYWORDS
    }


if __name__ == "__main__":
    kw = get_all_keywords()
    print(f"High    : {len(kw['high'])} keywords")
    print(f"Medium  : {len(kw['medium'])} keywords")
    print(f"Low     : {len(kw['low'])} keywords")
    print(f"Negative: {len(kw['negative'])} keywords")