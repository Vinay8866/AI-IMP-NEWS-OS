"""
AI IMP NEWS OS
RSS Feed Parser
Version: 5.0 - Fast + OG with Threading
"""

import hashlib
import re
from datetime import datetime
import feedparser
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except:
    HAS_BS4 = False

# Fast limit
MAX_PER_FEED = 15

def clean_html(text):
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def make_hash(title, link):
    raw = f"{title}|{link}".encode("utf-8")
    return hashlib.md5(raw).hexdigest()

def get_og_image_from_url(article_url):
    """Article ka OG image - fast 4 sec timeout"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(article_url, headers=headers, timeout=4, allow_redirects=True)
        if resp.status_code!= 200 or not HAS_BS4:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        for prop in ['og:image', 'twitter:image']:
            tag = soup.find('meta', property=prop) or soup.find('meta', attrs={'name': prop})
            if tag and tag.get('content','').startswith('http'):
                return tag.get('content')
        img = soup.find('img')
        if img and img.get('src','').startswith('http'):
            return img.get('src')
    except:
        pass
    return None

def extract_image(entry):
    """RSS se direct image"""
    if hasattr(entry, "media_content") and entry.media_content:
        for media in entry.media_content:
            url = media.get("url")
            if url and url.startswith("http"): return url
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get("url")
        if url and url.startswith("http"): return url
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type","").startswith("image"):
                return enc.get("href","")
    raw_html = entry.get('summary','') or entry.get('description','')
    if raw_html and HAS_BS4:
        try:
            soup = BeautifulSoup(raw_html, 'html.parser')
            img_tag = soup.find('img')
            if img_tag:
                src = img_tag.get('src') or img_tag.get('data-src')
                if src and src.startswith("http"): return src
        except: pass
    return None

def parse_feed(feed_url, source_name="", category=""):
    articles = []
    try:
        print(f" 📡 Fetching: {source_name or feed_url[:50]}...")
        feed = feedparser.parse(feed_url)
        if feed.bozo and not feed.entries:
            return articles

        # Pehle 15 hi lo
        temp_articles = []
        for entry in feed.entries[:MAX_PER_FEED]:
            title = clean_html(entry.get("title",""))
            link = entry.get("link","")
            if not title or not link: continue

            image = extract_image(entry)
            summary = clean_html(entry.get("summary","") or entry.get("description",""))
            if len(summary) > 400: summary = summary[:400]+"..."
            published = entry.get("published") or entry.get("updated") or datetime.now().strftime("%Y-%m-%d")

            temp_articles.append({
                "title": title, "link": link, "summary": summary,
                "published": published, "source": source_name,
                "category": category, "hash": make_hash(title, link),
                "image": image, "score": 0, "_needs_og": image is None
            })

        # Jinki image nahi hai unke liye OG ek saath fetch karo (fast threading)
        missing = [a for a in temp_articles if a["_needs_og"]]
        if missing:
            print(f" 🔍 {source_name}: {len(missing)} me image nahi, OG fetching (threaded)...")
            with ThreadPoolExecutor(max_workers=8) as executor:
                future_to_article = {executor.submit(get_og_image_from_url, art["link"]): art for art in missing}
                for future in as_completed(future_to_article):
                    art = future_to_article[future]
                    try:
                        og_img = future.result()
                        if og_img: art["image"] = og_img
                    except: pass

        # cleanup flag
        for art in temp_articles:
            art.pop("_needs_og", None)
            articles.append(art)

        with_image = len([a for a in articles if a['image']])
        print(f" ✅ {source_name}: {len(articles)} articles, {with_image} with images")

    except Exception as e:
        print(f" ❌ Error parsing {source_name}: {e}")
    return articles