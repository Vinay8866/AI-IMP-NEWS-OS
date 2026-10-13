"""
AI IMP NEWS OS
Confidence Calculator
Version: 2.0

Evidence के आधार पर confidence score (0-100) निकालता है।
"""


def calculate_confidence(evidence):
    """
    Confidence score formula:

    - Source credibility  (0-40 points)
    - Has valid link      (0-15 points)
    - Has summary         (0-15 points)
    - Has image           (0-10 points)
    - Claims count        (0-20 points)
    """
    if not evidence:
        return 0

    score = 0

    # Source credibility (map 0-100 → 0-40)
    credibility = evidence.get("source_credibility", 50)
    score += (credibility / 100) * 40

    # Has link
    if evidence.get("has_link"):
        score += 15

    # Has summary
    if evidence.get("has_summary"):
        score += 15

    # Has image
    if evidence.get("has_image"):
        score += 10

    # Claims count (max 20)
    claims = evidence.get("claims_count", 0)
    score += min(claims * 7, 20)

    return round(min(100, max(0, score)))


if __name__ == "__main__":
    tests = [
        {"source_credibility": 90, "has_link": True, "has_summary": True, "has_image": True, "claims_count": 3},
        {"source_credibility": 50, "has_link": True, "has_summary": False, "has_image": False, "claims_count": 1},
        {"source_credibility": 30, "has_link": False, "has_summary": False, "has_image": False, "claims_count": 0},
    ]
    for t in tests:
        print(f"Confidence: {calculate_confidence(t)}% ← {t}")