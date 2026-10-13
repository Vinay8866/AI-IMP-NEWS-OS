"""
AI IMP NEWS OS - App Settings
Version: 3.6 Buffer Edition - Social Queue & Scheduler
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # D:\AI-IMP-NEWS-OS
DB_PATH = BASE_DIR / "database" / "news.db"
CONTENT_DIR = BASE_DIR / "docs" / "content"
EVIDENCE_DIR = BASE_DIR / "docs" / "evidence"
PUBLISHED_DIR = BASE_DIR / "docs" / "published"
MEDIA_DIR = BASE_DIR / "media"
IMAGES_DIR = MEDIA_DIR / "images"
THUMBS_DIR = MEDIA_DIR / "thumbnails"
LOGS_DIR = BASE_DIR / "logs"

for d in [CONTENT_DIR, EVIDENCE_DIR, PUBLISHED_DIR, IMAGES_DIR, THUMBS_DIR, LOGS_DIR, DB_PATH.parent]:
    d.mkdir(parents=True, exist_ok=True)

APP_NAME = os.getenv("APP_NAME", "AI IMP NEWS OS")
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_MODEL_TEXT = os.getenv("GEMINI_MODEL_TEXT", "gemini-2.5-flash")

FREELLMAPI_API_KEY = os.getenv("FREELLMAPI_API_KEY", "")
FREELLMAPI_BASE_URL = os.getenv("FREELLMAPI_BASE_URL", "http://127.0.0.1:31415/v1")
FREELLMAPI_MODEL = os.getenv("FREELLMAPI_MODEL", "auto")

POLLINATIONS_URL = os.getenv("POLLINATIONS_URL", "https://image.pollinations.ai/prompt")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

MAX_RAW_NEWS = int(os.getenv("MAX_RAW_NEWS", "100"))
TOP_NEWS_COUNT = int(os.getenv("TOP_NEWS_COUNT", "6"))
QUALITY_PUBLISH_THRESHOLD = int(os.getenv("QUALITY_PUBLISH_THRESHOLD", "70"))
QUALITY_REWRITE_THRESHOLD = int(os.getenv("QUALITY_REWRITE_THRESHOLD", "50"))

# ============================================
# BUFFER CLONE - SOCIAL MEDIA SETTINGS
# ============================================
# Enable / Disable social auto-publishing
SOCIAL_ENABLED = os.getenv("SOCIAL_ENABLED", "true").lower() == "true"
SOCIAL_AUTO_SCHEDULE = os.getenv("SOCIAL_AUTO_SCHEDULE", "true").lower() == "true"

# Buffer-style optimal posting times (IST) - 3 slots daily
# User can change in frontend scheduler.html
SOCIAL_POST_TIMES = os.getenv("SOCIAL_POST_TIMES", '["08:00", "13:00", "19:00"]')
try:
    SOCIAL_POST_TIMES = json.loads(SOCIAL_POST_TIMES)
except:
    SOCIAL_POST_TIMES = ["08:00", "13:00", "19:00"]

# Default platforms to post
SOCIAL_DEFAULT_PLATFORMS = os.getenv("SOCIAL_DEFAULT_PLATFORMS", '["facebook", "instagram"]')
try:
    SOCIAL_DEFAULT_PLATFORMS = json.loads(SOCIAL_DEFAULT_PLATFORMS)
except:
    SOCIAL_DEFAULT_PLATFORMS = ["facebook", "instagram"]

# Facebook Graph API
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "")
FB_GRAPH_VERSION = os.getenv("FB_GRAPH_VERSION", "v19.0")

# Instagram (via Facebook Page)
IG_USER_ID = os.getenv("IG_USER_ID", "")  # Instagram Business Account ID
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", FB_PAGE_ACCESS_TOKEN)  # same as FB usually

# Buffer interval - check queue every N minutes
SOCIAL_CHECK_INTERVAL_MINUTES = int(os.getenv("SOCIAL_CHECK_INTERVAL_MINUTES", "2"))

# Caption style
SOCIAL_CAPTION_HASHTAGS = int(os.getenv("SOCIAL_CAPTION_HASHTAGS", "3"))
SOCIAL_ADD_LINK = os.getenv("SOCIAL_ADD_LINK", "false").lower() == "true"

def is_freellmapi_available():
    return bool(FREELLMAPI_API_KEY and FREELLMAPI_BASE_URL and "your-unified" not in FREELLMAPI_API_KEY.lower())

def is_gemini_available():
    return bool(GEMINI_API_KEY and "your_existing" not in GEMINI_API_KEY.lower())

def get_active_ai_provider():
    if is_freellmapi_available(): return "FreeLLMAPI"
    if is_gemini_available(): return "Gemini"
    return "Template"

def is_social_available():
    return bool(FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID) or not SOCIAL_ENABLED  # allow mock if disabled

def get_social_status():
    if not SOCIAL_ENABLED:
        return "Disabled (Mock Mode)"
    if FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID:
        return f"Facebook + Instagram Ready ({FB_GRAPH_VERSION})"
    return "Mock Mode (No FB tokens - will simulate posting)"
