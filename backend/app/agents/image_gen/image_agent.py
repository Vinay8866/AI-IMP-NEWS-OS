# """
# AI IMP NEWS OS
# Image Agent
# Version: 2.0

# Abhi production-safe mode:
# 1) Strong image prompt banata hai
# 2) Placeholder image save karta hai (Pillow)
# 3) Future me real image API plug kar sakte ho
# """

# from pathlib import Path
# from datetime import datetime

# from app.agents.image_gen.prompt_builder import build_image_prompt
# from app.config.settings import IMAGES_DIR, GEMINI_API_KEY


# class ImageAgent:
#     def __init__(self):
#         IMAGES_DIR.mkdir(parents=True, exist_ok=True)

#     def generate_prompt(self, title, category=""):
#         return build_image_prompt(title, category)

#     def _make_placeholder_image(self, slug, title):
#         """Pillow se simple placeholder PNG banao"""
#         try:
#             from PIL import Image, ImageDraw, ImageFont

#             width, height = 1280, 720
#             img = Image.new("RGB", (width, height), color=(108, 92, 231))
#             draw = ImageDraw.Draw(img)

#             # Soft panel
#             draw.rounded_rectangle((80, 120, width - 80, height - 120), radius=40, fill=(255, 255, 255))

#             text = title[:70] + ("..." if len(title) > 70 else "")
#             try:
#                 font = ImageFont.truetype("arial.ttf", 36)
#                 small = ImageFont.truetype("arial.ttf", 22)
#             except Exception:
#                 font = ImageFont.load_default()
#                 small = ImageFont.load_default()

#             draw.text((120, 220), "AI IMP NEWS OS", fill=(108, 92, 231), font=small)
#             draw.text((120, 280), text, fill=(26, 26, 46), font=font)
#             draw.text((120, 500), "Auto-generated placeholder image", fill=(100, 116, 139), font=small)

#             out_path = IMAGES_DIR / f"{slug}.png"
#             img.save(out_path, format="PNG")
#             return str(out_path)
#         except Exception as e:
#             print(f"  ⚠️  Placeholder image failed: {e}")
#             return ""

#     def generate(self, title, slug="", category=""):
#         """
#         Returns dict:
#         - prompt
#         - status
#         - path
#         """
#         slug = slug or f"news-{datetime.now().strftime('%H%M%S')}"
#         prompt = self.generate_prompt(title, category)

#         # NOTE: Real image generation providers vary by account/API.
#         # Yahan stable placeholder + prompt save karte hain taaki pipeline full chale.
#         path = self._make_placeholder_image(slug, title)
#         status = "placeholder_ready" if path else "prompt_only"

#         if GEMINI_API_KEY:
#             # Key present hai, future real generation ke liye ready
#             status = status  # keep as-is for now

#         return {
#             "prompt": prompt,
#             "status": status,
#             "path": path
#         }


# if __name__ == "__main__":
#     agent = ImageAgent()
#     result = agent.generate("AI transforms marketing automation", slug="ai-marketing-test", category="AI")
#     print(result)













"""
AI IMP NEWS OS - Image Agent
Version: 3.0 - Real Pollinations AI Image + Fallback
"""
from pathlib import Path
from datetime import datetime
import urllib.parse
import httpx
from app.agents.image_gen.prompt_builder import build_image_prompt
from app.config.settings import IMAGES_DIR, POLLINATIONS_URL

class ImageAgent:
    def __init__(self):
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    def generate_prompt(self, title, category=""):
        return build_image_prompt(title, category)

    def _make_placeholder_image(self, slug, title):
        try:
            from PIL import Image, ImageDraw, ImageFont
            width, height = 1280, 720
            img = Image.new("RGB", (width, height), color=(108, 92, 231))
            draw = ImageDraw.Draw(img)
            draw.rounded_rectangle((80, 120, width-80, height-120), radius=40, fill=(255, 255, 255))
            text = title[:70]
            try:
                font = ImageFont.truetype("arial.ttf", 36)
                small = ImageFont.truetype("arial.ttf", 22)
            except:
                font = ImageFont.load_default()
                small = ImageFont.load_default()
            draw.text((120, 220), "AI IMP NEWS OS", fill=(108, 92, 231), font=small)
            draw.text((120, 280), text, fill=(26, 26, 46), font=font)
            out_path = IMAGES_DIR / f"{slug}.png"
            img.save(out_path, format="PNG")
            return str(out_path)
        except Exception as e:
            print(f" Placeholder failed: {e}")
            return ""

    def _generate_real_image(self, prompt_text, slug):
        try:
            encoded = urllib.parse.quote(prompt_text[:800])
            base = POLLINATIONS_URL.strip().rstrip('/')
            if base.endswith('/prompt'):
                url = f"{base}/{encoded}?width=1280&height=720&nologo=true&model=flux&enhance=true"
            else:
                url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true&model=flux&enhance=true"
            print(f" [*] Pollinations: {url[:90]}...")
            out_path = IMAGES_DIR / f"{slug}.jpg"
            with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                r = client.get(url)
                if r.status_code == 200 and len(r.content) > 10000:
                    out_path.write_bytes(r.content)
                    print(f" [ok] Real image: {out_path}")
                    return str(out_path)
        except Exception as e:
            print(f" [x] Real image error: {e}")
        return ""

    def generate(self, title, slug="", category=""):
        slug = slug or f"news-{datetime.now().strftime('%H%M%S')}"
        prompt = self.generate_prompt(title, category)
        real_path = self._generate_real_image(prompt, slug)
        if real_path:
            return {"prompt": prompt, "status": "generated", "path": real_path}
        path = self._make_placeholder_image(slug, title)
        status = "placeholder_ready" if path else "prompt_only"
        return {"prompt": prompt, "status": status, "path": path}