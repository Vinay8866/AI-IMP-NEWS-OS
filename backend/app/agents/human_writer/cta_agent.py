"""
AI IMP NEWS OS
CTA Agent
Version: 2.0

Short call-to-action line banata hai.
"""


def generate_cta(category=""):
    """Category ke hisaab se soft CTA"""
    category = (category or "").lower()

    if "seo" in category:
        return "If you work in SEO, test how this change affects your next content sprint."
    if "marketing" in category:
        return "Marketing teams should review this update and adapt campaigns where needed."
    if "ai" in category or "technology" in category:
        return "Follow this space — practical AI and tech shifts like this can reshape workflows fast."
    if "social" in category:
        return "Social teams can use this as a cue to refine posting strategy this week."

    return "Stay curious, verify details, and apply only what fits your goals."


if __name__ == "__main__":
    print(generate_cta("AI"))
    print(generate_cta("SEO"))