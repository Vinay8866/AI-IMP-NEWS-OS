"""
AI IMP NEWS OS
SEO Agent
Version: 2.0

Slug, meta title, meta description banata hai.
"""

import re


def slugify(text):
    """URL-safe slug"""
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80] if text else "untitled"


class SEOAgent:
    def generate(self, title, hook="", story=""):
        title = title or "Untitled Article"
        hook = hook or ""
        story = story or ""

        slug = slugify(title)

        # Meta title max ~60 chars
        meta_title = title.strip()
        if len(meta_title) > 60:
            meta_title = meta_title[:57] + "..."

        # Meta description max ~155 chars
        base = hook if hook else story
        base = re.sub(r"\s+", " ", base).strip()
        if not base:
            base = f"Read the latest update: {title}"
        meta_description = base[:152] + ("..." if len(base) > 152 else "")

        # Simple keywords from title
        words = [w for w in re.findall(r"[a-zA-Z0-9]+", title.lower()) if len(w) > 3]
        keywords = list(dict.fromkeys(words))[:8]

        return {
            "slug": slug,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "keywords": keywords
        }


if __name__ == "__main__":
    agent = SEOAgent()
    data = agent.generate(
        "OpenAI launches new ChatGPT marketing tools",
        hook="A practical update that marketers should not ignore."
    )
    print(data)