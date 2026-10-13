"""
AI IMP NEWS OS
Evidence Gatherer
Version: 2.0

Basic evidence gathering - source credibility check.
(Advanced version later: cross-reference multiple sources via Gemini)
"""

# Trusted sources get higher credibility
TRUSTED_SOURCES = {
    "techcrunch": 90,
    "the verge": 85,
    "wired": 85,
    "google news": 80,
    "hubspot": 80,
    "search engine journal": 85,
    "social media today": 75,
    "martech": 75,
    "marketing land": 75,
}

DEFAULT_CREDIBILITY = 50


def get_source_credibility(source_name):
    """Source का credibility score (0-100)"""
    if not source_name:
        return DEFAULT_CREDIBILITY

    name_lower = source_name.lower()
    for key, score in TRUSTED_SOURCES.items():
        if key in name_lower:
            return score
    return DEFAULT_CREDIBILITY


def find_evidence(article, claims_data):
    """
    Article के लिए evidence gather करो।

    Returns evidence dict with credibility info.
    """
    source = article.get("source", "")
    credibility = get_source_credibility(source)

    has_link = bool(article.get("link"))
    has_summary = bool(article.get("summary")) and len(article.get("summary", "")) > 30
    has_image = bool(article.get("image"))
    claims_count = len(claims_data.get("claims", []))

    evidence = {
        "source": source,
        "source_credibility": credibility,
        "has_link": has_link,
        "has_summary": has_summary,
        "has_image": has_image,
        "claims_count": claims_count,
        "link": article.get("link", ""),
        "keywords": claims_data.get("keywords", []),
    }

    return evidence


if __name__ == "__main__":
    test_article = {"source": "TechCrunch", "link": "https://example.com", "summary": "A" * 50, "image": None}
    test_claims = {"claims": ["claim1", "claim2"], "keywords": ["AI", "OpenAI"]}
    ev = find_evidence(test_article, test_claims)
    print(ev)