# """
# AI IMP NEWS OS
# Story Agent
# Version: 3.0 (FreeLLMAPI Primary + Gemini Backup + Template)

# Full humanized blog story likhta hai.
# Priority: FreeLLMAPI -> Gemini -> Template
# """

# from app.agents.ai_client import generate
# from app.config.settings import GEMINI_API_KEY, GEMINI_MODEL_TEXT


# def _build_prompt(title, summary, claims, source):
#     claims_text = ""
#     if claims:
#         if isinstance(claims, list):
#             claims_text = "\n".join(f"- {c}" for c in claims[:5])
#         else:
#             claims_text = str(claims)

#     return f"""Write a clear, human-sounding blog article about this news.

# Title: {title}
# Source: {source}
# Summary: {summary[:400]}
# Key points:
# {claims_text}

# Rules:
# - 180 to 280 words
# - Simple English, easy to read
# - Structure: intro, what happened, why it matters, short conclusion
# - Do NOT invent facts not in the summary
# - No markdown headings, plain paragraphs only
# - Return ONLY the article body
# """


# def write_story_with_gemini(title, summary="", claims=None, source=""):
#     """Direct Gemini se full story likho (backup only)"""
#     try:
#         import google.generativeai as genai
#         genai.configure(api_key=GEMINI_API_KEY)
#         model = genai.GenerativeModel(GEMINI_MODEL_TEXT)

#         prompt = _build_prompt(title, summary, claims, source)
#         response = model.generate_content(prompt)
#         story = response.text.strip()
#         if story and len(story) > 80:
#             return story
#     except Exception as e:
#         print(f"  ⚠️  Gemini story failed: {e}")
#     return None


# def write_story_template(title, summary="", source=""):
#     """Fallback story bina AI ke"""
#     summary_text = summary.strip() if summary else "Details are still emerging."
#     source_text = source if source else "industry reports"

#     story = (
#         f"{title}. According to {source_text}, this development is drawing attention "
#         f"across the market and marketing technology space.\n\n"
#         f"{summary_text}\n\n"
#         f"For teams watching technology, AI, SEO, and digital growth, this update is "
#         f"useful context. It highlights how quickly tools, platforms, and strategies "
#         f"are shifting — and why staying informed matters.\n\n"
#         f"The takeaway is simple: track the change, understand the impact, and decide "
#         f"what action (if any) fits your goals. We will continue monitoring related updates."
#     )
#     return story


# def write_story(title, verification_data=None):
#     """
#     Main story function. Priority: FreeLLMAPI -> Gemini -> Template
#     verification_data dict ho sakta hai (title, summary, source, claims)
#     """
#     if verification_data is None:
#         verification_data = {}

#     title = title or verification_data.get("title", "Untitled")
#     summary = verification_data.get("summary", "")
#     source = verification_data.get("source", "")
#     claims = verification_data.get("claims", [])

#     # TRY 1: FreeLLMAPI (PRIMARY)
#     prompt = _build_prompt(title, summary, claims, source)
#     story = generate(prompt=prompt, task_name="Story Writing")

#     if story and len(story.strip()) > 80:
#         return story.strip()

#     # TRY 2: Direct Gemini (BACKUP)
#     if GEMINI_API_KEY:
#         story = write_story_with_gemini(title, summary, claims, source)
#         if story:
#             return story

#     # TRY 3: Template (LAST RESORT)
#     return write_story_template(title, summary, source)


# if __name__ == "__main__":
#     data = {
#         "title": "Google updates Search algorithm for AI content",
#         "summary": "Google announced changes that reward helpful original content.",
#         "source": "Search Engine Journal",
#         "claims": ["Google updated ranking signals", "Helpful content preferred"]
#     }
#     story = write_story(data["title"], data)
#     print(story[:500])
#     print(f"\n... ({len(story)} chars)")







"""
AI IMP NEWS OS - Story Agent
Version: 3.5 (Clean - No Direct Gemini Import)
"""
from app.agents.ai_client import generate

def write_story_template(title, verification_data):
    summary = verification_data.get("summary", "") if verification_data else ""
    source = verification_data.get("source", "Unknown") if verification_data else "Unknown"
    base = summary if summary else title
    story = f"""{base}

This development has caught attention across the industry. While details are still emerging, the core update points to a shift in how teams approach this area.

Key points to note:
- What changed and why it matters
- Who is impacted
- What to watch next

Source: {source}. As always, verify critical details before acting on them.
"""
    return story.strip()

def write_story(title, verification_data=None):
    verification_data = verification_data or {}
    summary = verification_data.get("summary", "")
    source = verification_data.get("source", "")
    claims = verification_data.get("claims", [])

    prompt = f"""Write a clear, human-written news article (150-220 words) for this verified news.

Title: {title}
Summary: {summary}
Source: {source}
Claims: {claims}

Rules:
- Write in simple, professional English
- No hype, no fake data
- 2-3 short paragraphs
- End with a practical takeaway
- Return ONLY the story text
"""
    story = generate(prompt=prompt, task_name="Story Writing")
    if story and len(story) > 80:
        story = story.strip().strip('"').strip("'")
        if story.lower().startswith("story:"):
            story = story.split(":", 1)[1].strip()
        return story
    return write_story_template(title, verification_data)