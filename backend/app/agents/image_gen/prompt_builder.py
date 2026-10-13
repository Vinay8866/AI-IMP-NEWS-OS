"""
AI IMP NEWS OS
Image Prompt Builder
Version: 2.0
"""


def build_image_prompt(title, category="", style="modern tech illustration"):
    """News se image generation prompt banao"""
    title = title or "Technology news update"
    category = category or "technology"

    prompt = (
        f"Create a clean {style} for a news article about: '{title}'. "
        f"Category: {category}. "
        f"Style: minimal, professional, high-quality, claymorphism soft UI look, "
        f"no text in image, no watermark, 16:9 composition, vibrant but soft colors."
    )
    return prompt


if __name__ == "__main__":
    print(build_image_prompt("AI transforms digital marketing", "AI"))