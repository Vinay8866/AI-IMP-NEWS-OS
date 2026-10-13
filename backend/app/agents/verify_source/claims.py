"""
AI IMP NEWS OS
Claims Extractor
Version: 2.0

News title + summary से key claims/keywords निकालता है।
"""

import re


def extract_claims(article):
    """
    Article से key claims निकालो।

    Simple approach (no AI needed for basic version):
    - Important nouns/phrases from title
    - Key sentences from summary
    """
    title = article.get("title", "")
    summary = article.get("summary", "")

    claims = []

    # Title itself is the main claim
    if title:
        claims.append(title)

    # Extract potential key phrases (Capitalized words sequences)
    if summary:
        # Split into sentences
        sentences = re.split(r"[.!?]+", summary)
        for sent in sentences[:3]:  # max 3 sentences
            sent = sent.strip()
            if len(sent) > 20:
                claims.append(sent)

    # Extract named-entity-like words (capitalized)
    words = re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", title)
    keywords = list(set(words))

    return {
        "claims": claims[:5],
        "keywords": keywords[:10],
        "claims_text": " | ".join(claims[:3])
    }


if __name__ == "__main__":
    test = {
        "title": "OpenAI Launches GPT-5 with Revolutionary Features",
        "summary": "OpenAI has announced GPT-5. The new model shows major improvements. Industry experts are impressed."
    }
    result = extract_claims(test)
    print("Claims:", result["claims"])
    print("Keywords:", result["keywords"])