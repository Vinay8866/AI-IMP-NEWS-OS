# """
# AI IMP NEWS OS
# Hook Agent
# Version: 3.0 (FreeLLMAPI Primary + Gemini Backup + Template)

# News title se attractive opening hook banata hai.
# Priority: FreeLLMAPI -> Gemini -> Template
# """

# from app.agents.ai_client import generate
# from app.config.settings import GEMINI_API_KEY, GEMINI_MODEL_TEXT


# def generate_hook_with_gemini(title, summary=""):
#     """Direct Gemini se hook generate karo (backup only)"""
#     try:
#         import google.generativeai as genai
#         genai.configure(api_key=GEMINI_API_KEY)
#         model = genai.GenerativeModel(GEMINI_MODEL_TEXT)

#         prompt = f"""Write a short, catchy opening hook (1-2 sentences max) for a blog post about this news.

# Title: {title}
# Summary: {summary[:200]}

# Rules:
# - Make it engaging and human
# - No clickbait lies
# - Max 40 words
# - Return ONLY the hook text, nothing else
# """
#         response = model.generate_content(prompt)
#         hook = response.text.strip().strip('"').strip("'")
#         if hook and len(hook) > 10:
#             return hook
#     except Exception as e:
#         print(f"  ⚠️  Gemini hook failed: {e}")
#     return None


# def generate_hook_template(title):
#     """Fallback template hooks (bina AI ke)"""
#     templates = [
#         f"Here's what you need to know: {title}",
#         f"Big move in the industry — {title}",
#         f"This just happened and it matters: {title}",
#         f"Breaking down the latest update: {title}",
#         f"Why everyone is talking about this: {title}",
#     ]
#     idx = len(title) % len(templates)
#     return templates[idx]


# def generate_hook(title, summary=""):
#     """
#     Main function — Priority: FreeLLMAPI -> Gemini -> Template
#     """

#     # TRY 1: FreeLLMAPI (PRIMARY - FREE 7.4B tokens/month)
#     prompt = f"""Write a short, catchy opening hook (1-2 sentences max) for a blog post about this news.

# Title: {title}
# Summary: {summary[:200]}

# Rules:
# - Make it engaging and human
# - No clickbait lies
# - Max 40 words
# - Return ONLY the hook text, nothing else
# """
#     hook = generate(prompt=prompt, task_name="Hook Generation")

#     if hook:
#         hook = hook.strip().strip('"').strip("'")
#         if hook.lower().startswith("hook:"):
#             hook = hook.split(":", 1)[1].strip()
#         if len(hook) > 10:
#             return hook

#     # TRY 2: Direct Gemini (BACKUP)
#     if GEMINI_API_KEY:
#         hook = generate_hook_with_gemini(title, summary)
#         if hook:
#             return hook

#     # TRY 3: Template (LAST RESORT)
#     return generate_hook_template(title)


# if __name__ == "__main__":
#     test_title = "OpenAI launches new ChatGPT features for marketers"
#     test_summary = "The new update includes better analytics and content tools."
#     hook = generate_hook(test_title, test_summary)
#     print(f"Hook: {hook}")





"""
AI IMP NEWS OS - Hook Agent
Version: 3.5 (Clean - No Direct Gemini Import)
"""
from app.agents.ai_client import generate

def generate_hook_template(title):
    templates = [
        f"Here's what you need to know: {title}",
        f"Big move in the industry — {title}",
        f"This just happened and it matters: {title}",
        f"Breaking down the latest update: {title}",
        f"Why everyone is talking about this: {title}",
    ]
    idx = len(title) % len(templates)
    return templates[idx]

def generate_hook(title, summary=""):
    prompt = f"""Write a short, catchy opening hook (1-2 sentences max) for a blog post.

Title: {title}
Summary: {summary[:200]}

Rules:
- Make it engaging and human
- No clickbait lies
- Max 40 words
- Return ONLY the hook text, nothing else
"""
    hook = generate(prompt=prompt, task_name="Hook Generation")
    if hook:
        hook = hook.strip().strip('"').strip("'")
        if hook.lower().startswith("hook:"):
            hook = hook.split(":", 1)[1].strip()
        if len(hook) > 10:
            return hook
    return generate_hook_template(title)