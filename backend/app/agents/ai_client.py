"""
AI IMP NEWS OS
Central AI Client — FreeLLMAPI + Gemini + Template Fallback
Version: v3.2 (Optimized Timeouts, Robust Retries & Silence Legacy Warnings)
"""

import time
import httpx
import warnings
from app.config import settings

# Suppress the deprecation warning from google-generativeai cleanly
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")


def generate(prompt: str, task_name: str = "AI Task", max_retries: int = 2) -> str:
    # 1. Try FreeLLMAPI (Primary)
    if settings.is_freellmapi_available():
        result = _call_freellmapi(prompt, task_name, max_retries)
        if result:
            return result

    # 2. Try Gemini (Backup)
    if settings.is_gemini_available():
        result = _call_gemini(prompt, task_name, max_retries)
        if result:
            return result

    # 3. Template Fallback
    print(f"  [!] {task_name}: Using template fallback")
    return _generate_template(prompt, task_name)


def _call_freellmapi(prompt: str, task_name: str, max_retries: int) -> str:
    url = f"{settings.FREELLMAPI_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.FREELLMAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.FREELLMAPI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional news writer. Write concisely and factually in English."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    # Setup robust timeout architecture (allowing longer wait times for cold boot models)
    timeout_config = httpx.Timeout(90.0, connect=15.0, read=75.0, write=15.0)

    for attempt in range(1, max_retries + 1):
        try:
            print(f"  [*] {task_name}: FreeLLMAPI attempt {attempt}...")
            response = httpx.post(url, headers=headers, json=payload, timeout=timeout_config)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                routed = response.headers.get("x-routed-via", "unknown")
                print(f"  [ok] {task_name}: Success via {routed}")
                return content.strip()
                
            elif response.status_code == 429:
                print(f"  [!] {task_name}: Rate Limit (429) hit. Cooling down...")
                time.sleep(5)
            else:
                print(f"  [x] {task_name}: Server responded with status code {response.status_code}")
                time.sleep(3)
                
        except httpx.TimeoutException:
            print(f"  [x] {task_name}: FreeLLMAPI attempt {attempt} timed out.")
            time.sleep(3)
        except Exception as e:
            print(f"  [x] {task_name}: FreeLLMAPI attempt {attempt} connection error: {e}")
            time.sleep(3)
            
    return ""


def _call_gemini(prompt: str, task_name: str, max_retries: int) -> str:
    """Safe hybrid client supporting both Modern google-genai and Legacy SDK packages."""
    # Attempt 1: Modern google-genai client
    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        for attempt in range(1, max_retries + 1):
            try:
                print(f"  [*] {task_name}: Gemini (Modern SDK) attempt {attempt}...")
                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt
                )
                if response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"  [x] {task_name}: Gemini Modern error on attempt {attempt}: {e}")
                time.sleep(3)
        return ""
    except ImportError:
        # Fallback silently to Legacy generativeai client if modern SDK is not installed
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            for attempt in range(1, max_retries + 1):
                try:
                    print(f"  [*] {task_name}: Gemini (Legacy SDK) attempt {attempt}...")
                    res = model.generate_content(prompt)
                    if res.text:
                        return res.text.strip()
                except Exception as e:
                    print(f"  [x] {task_name}: Gemini Legacy error on attempt {attempt}: {e}")
                    time.sleep(3)
        except Exception as e:
            print(f"  [x] {task_name}: Gemini legacy client initialization failed: {e}")
    return ""


def _generate_template(prompt: str, task_name: str) -> str:
    task_lower = task_name.lower()
    if "hook" in task_lower:
        return "Breaking industry update: Crucial developments are unfolding rapidly today."
    elif "story" in task_lower:
        return "Key market leaders have announced critical operational shifts. The impact is expanding across technology sectors globally with lasting implications."
    elif "cta" in task_lower:
        return "Stay updated on global tech movements. Follow our AI channel for verified daily news."
    return "Verified factual industry report."


if __name__ == "__main__":
    print("Testing AI Client...")
    print(generate("Write a 1-line news headline about AI chips.", "Test"))