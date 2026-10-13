"""
AI IMP NEWS OS
Social Publisher - Buffer Clone Engine
Version: 3.0

Real Facebook Graph API + Instagram + Mock Mode
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

from app.config.settings import (
    FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN, FB_GRAPH_VERSION,
    IG_USER_ID, IG_ACCESS_TOKEN,
    SOCIAL_ENABLED, PUBLISHED_DIR, IMAGES_DIR
)


class SocialPublisher:
    """Buffer-style Publisher"""

    def __init__(self):
        self.fb_page_id = FB_PAGE_ID
        self.fb_token = FB_PAGE_ACCESS_TOKEN
        self.ig_user_id = IG_USER_ID
        self.ig_token = IG_ACCESS_TOKEN or FB_PAGE_ACCESS_TOKEN
        self.graph_version = FB_GRAPH_VERSION
        self.enabled = SOCIAL_ENABLED

    def is_real_mode(self):
        return bool(self.fb_page_id and self.fb_token and self.enabled)

    def publish(self, social_row):
        """
        social_row: dict from social_schedule table
        Returns: {"facebook": post_id or error, "instagram": post_id or error}
        """
        caption = social_row.get("caption", "")
        image_path = social_row.get("image_path", "")
        platforms = json.loads(social_row.get("platforms", '["facebook"]')) if isinstance(social_row.get("platforms"), str) else social_row.get("platforms", ["facebook"])

        # Resolve image
        image_full_path = self.resolve_image_path(image_path, social_row)

        results = {}

        if not self.is_real_mode():
            # MOCK MODE - simulate posting
            print(f"\n[SocialPublisher MOCK] Publishing ID {social_row['id']}")
            print(f"  Platforms: {platforms}")
            print(f"  Caption: {caption[:100]}...")
            print(f"  Image: {image_full_path}")
            mock_id = f"mock_{social_row['id']}_{datetime.now().strftime('%H%M%S')}"
            for plat in platforms:
                results[plat] = mock_id
            # Log to file for proof
            self.log_mock_post(social_row, platforms, image_full_path)
            return {"success": True, "results": results, "mode": "mock"}

        # REAL MODE
        try:
            if "facebook" in platforms:
                fb_id = self.post_to_facebook(caption, image_full_path)
                results["facebook"] = fb_id

            if "instagram" in platforms:
                # Instagram needs image URL or container
                # For local images, we need to upload first - for now use FB photo then share? Simplified: require image
                if image_full_path and os.path.exists(image_full_path):
                    ig_id = self.post_to_instagram(caption, image_full_path)
                    results["instagram"] = ig_id
                else:
                    results["instagram"] = {"error": "No image for Instagram"}

            return {"success": True, "results": results, "mode": "real"}

        except Exception as e:
            print(f"[SocialPublisher] Error: {e}")
            return {"success": False, "error": str(e), "results": results}

    def resolve_image_path(self, image_path, social_row):
        """Image path ko full path me convert"""
        if not image_path:
            # Try to find latest generated image for this article
            # Look in media/images
            try:
                from pathlib import Path
                if IMAGES_DIR.exists():
                    # Get latest image
                    images = sorted(IMAGES_DIR.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
                    if images:
                        return str(images[0])
            except:
                pass
            return None

        p = Path(image_path)
        if p.is_absolute() and p.exists():
            return str(p)

        # Try relative to BASE_DIR
        from app.config.settings import BASE_DIR
        candidates = [
            BASE_DIR / image_path,
            BASE_DIR / "media" / "images" / Path(image_path).name,
            BASE_DIR / "docs" / "content" / image_path,
            Path(image_path)
        ]
        for c in candidates:
            if c.exists():
                return str(c)
        return image_path

    def post_to_facebook(self, caption, image_path=None):
        """Post to Facebook Page"""
        url = f"https://graph.facebook.com/{self.graph_version}/{self.fb_page_id}/photos"
        data = {
            "caption": caption,
            "access_token": self.fb_token
        }

        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                files = {"source": f}
                resp = requests.post(url, data=data, files=files, timeout=30)
        else:
            # Text only post
            url = f"https://graph.facebook.com/{self.graph_version}/{self.fb_page_id}/feed"
            data = {"message": caption, "access_token": self.fb_token}
            resp = requests.post(url, data=data, timeout=30)

        print(f"[FB Response] {resp.status_code}: {resp.text[:200]}")
        resp.raise_for_status()
        result = resp.json()
        return result.get("post_id") or result.get("id")

    def post_to_instagram(self, caption, image_path):
        """Post to Instagram - 2 step: create container + publish"""
        if not self.ig_user_id:
            raise Exception("IG_USER_ID not set")

        # Step 1: Upload image to FB and get URL? For simplicity, we try direct container creation
        # Instagram Graph API needs image_url publicly accessible. For local dev, we upload to Facebook first
        # Workaround: upload image as FB photo and use its URL? Better: use base64? But API needs URL.
        # For this clone, we will upload to imgur-like pollinations or just skip if no URL
        # Simpler: create container with image_url from local file via upload to Facebook's staging?

        # For MVP: try to post with local file upload via creation
        # Note: IG API doesn't support direct file upload in container, needs URL. So we mock if no public URL.
        # We'll attempt with caption only if image not accessible, but Instagram requires image.

        # Alternative: if we have FB photo id from previous step, use it?
        # For now, attempt container creation with caption, assuming image is hosted elsewhere
        # If you have public image URL (POLLINATIONS_URL), it would work.

        # Try to get public image URL - if image_path is from pollinations, use it
        # Else, upload image to facebook and get link? We'll use mock for local images

        # Check if image_path is URL
        if image_path and image_path.startswith("http"):
            image_url = image_path
        else:
            # No public URL, can't post to IG in real mode without hosting. Return mock logic or error
            # For real implementation, host image to S3 / public URL first
            raise Exception(f"Instagram requires public image URL, local file found: {image_path}. Host it first or use mock mode.")

        # Step 1: Create container
        container_url = f"https://graph.facebook.com/{self.graph_version}/{self.ig_user_id}/media"
        data = {
            "caption": caption,
            "image_url": image_url,
            "access_token": self.ig_token
        }
        resp = requests.post(container_url, data=data, timeout=30)
        print(f"[IG Container] {resp.status_code}: {resp.text[:200]}")
        resp.raise_for_status()
        container_id = resp.json().get("id")

        # Step 2: Publish container
        publish_url = f"https://graph.facebook.com/{self.graph_version}/{self.ig_user_id}/media_publish"
        data2 = {
            "creation_id": container_id,
            "access_token": self.ig_token
        }
        resp2 = requests.post(publish_url, data=data2, timeout=30)
        print(f"[IG Publish] {resp2.status_code}: {resp2.text[:200]}")
        resp2.raise_for_status()
        return resp2.json().get("id")

    def log_mock_post(self, social_row, platforms, image_path):
        """Mock posts ko file me log karo proof ke liye"""
        log_dir = PUBLISHED_DIR / "social_mock"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{social_row['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = {
            "id": social_row["id"],
            "title": social_row.get("title"),
            "caption": social_row.get("caption"),
            "platforms": platforms,
            "image_path": image_path,
            "scheduled_at": social_row.get("scheduled_at"),
            "mock_posted_at": datetime.now().isoformat(),
            "status": "mock_posted"
        }
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[Mock Log] Saved to {log_file}")
