"""
AI IMP NEWS OS
Fact Check Agent
Version: 2.0

Basic fact consistency checks.
"""


def fact_check(verification_data):
    """
    Simple fact checks:
    - confidence available?
    - claims present?
    - source present?
    - summary present?
    """
    if not verification_data:
        return {
            "passed": False,
            "score": 0,
            "notes": ["No verification data"]
        }

    notes = []
    score = 100

    confidence = verification_data.get("confidence", 0)
    claims = verification_data.get("claims", [])
    source = verification_data.get("source", "")
    summary = verification_data.get("summary", "")
    title = verification_data.get("title", "")

    if confidence < 40:
        score -= 30
        notes.append("Low confidence score")
    elif confidence < 70:
        score -= 10
        notes.append("Medium confidence score")
    else:
        notes.append("Confidence OK")

    if not claims:
        score -= 15
        notes.append("No claims extracted")
    else:
        notes.append(f"Claims found: {len(claims)}")

    if not source:
        score -= 10
        notes.append("Missing source")
    else:
        notes.append("Source present")

    if not summary or len(summary) < 20:
        score -= 15
        notes.append("Weak/missing summary")
    else:
        notes.append("Summary present")

    if not title:
        score -= 20
        notes.append("Missing title")

    score = max(0, min(100, score))
    passed = score >= 60

    return {
        "passed": passed,
        "score": score,
        "notes": notes
    }


if __name__ == "__main__":
    test = {
        "title": "AI news example",
        "summary": "This is a valid summary with enough text.",
        "source": "TechCrunch",
        "confidence": 76,
        "claims": ["claim one", "claim two"]
    }
    print(fact_check(test))